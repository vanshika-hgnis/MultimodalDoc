import fitz
import pdfplumber
import tempfile
from supabase_client import supabase
from ocr_service import get_ocr_reader
import re


def table_to_markdown(table):
    rows = []
    for row in table:
        rows.append([("" if c is None else str(c)).strip() for c in row])

    if not rows:
        return ""

    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    md = "| " + " | ".join(header) + " |\n"
    md += "| " + " | ".join(["---"] * len(header)) + " |\n"

    for r in body:
        r = (r + [""] * len(header))[:len(header)]
        md += "| " + " | ".join(r) + " |\n"

    return md




def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove other invisible control characters except newline and tab
    text = re.sub(r"[\x01-\x08\x0B-\x1F\x7F]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def clean_table_json(table):
    cleaned = []

    for row in table:
        cleaned_row = []
        for cell in row:
            if cell is None:
                cleaned_row.append("")
            else:
                cleaned_row.append(clean_text(str(cell)))
        cleaned.append(cleaned_row)

    return cleaned



def is_good_block(text: str) -> bool:
    t = text.strip()

    if len(t) < 30:
        return False

    digits = sum(ch.isdigit() for ch in t)
    if digits / max(len(t), 1) > 0.45:
        return False

    alpha = sum(ch.isalpha() for ch in t)
    if alpha < 20:
        return False

    bad_patterns = [
        r"notes located on\s+page",
        r"self-contained year-end statement",
    ]

    for p in bad_patterns:
        if re.search(p, t, re.IGNORECASE):
            return False

    return True


def ingest_document(document_id: str):

    # 1️⃣ Get document metadata
    doc_response = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .execute()
    )

    if not doc_response.data:
        raise Exception("Document not found")

    storage_path = doc_response.data[0]["storage_path"]

    response = supabase.storage.from_("documents").download(storage_path)

    if not response:
        raise Exception("Failed to download from storage")

    # 2️⃣ Write temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response)
        tmp_path = tmp.name

    # 3️⃣ Open PDFs
    pdf = fitz.open(tmp_path)
    plumber_pdf = pdfplumber.open(tmp_path)

    # 4️⃣ Loop through pages
    for page_number in range(len(pdf)):

        page = pdf[page_number]
        plumber_page = plumber_pdf.pages[page_number]

        blocks = page.get_text("blocks")

        page_text_content = " ".join(
            [b[4] for b in blocks if b[4] and b[4].strip()]
        )

        # -----------------------
        # TEXT EXTRACTION
        # -----------------------

        if page_text_content.strip():
            for block in blocks:
                x0, y0, x1, y1 = block[:4]
                # text = block[4]
                text = clean_text(block[4])

                if text and is_good_block(text):
                    supabase.table("text_blocks").insert({
                        "document_id": document_id,
                        "page_number": page_number + 1,
                        "text": text,
                        "bbox": {
                            "x0": x0,
                            "y0": y0,
                            "x1": x1,
                            "y1": y1
                        },
                        "source_type": "pdf_text"
                    }).execute()

        else:
            # -----------------------
            # OCR FALLBACK
            # -----------------------

            reader = get_ocr_reader()

            pix = page.get_pixmap(dpi=300)
            image_bytes = pix.tobytes("png")

            results = reader.readtext(image_bytes)

            for bbox, text, prob in results:
                text = clean_text(text)
                if not text.strip():
                    continue

                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]

                supabase.table("text_blocks").insert({
                    "document_id": document_id,
                    "page_number": page_number + 1,
                    "text": text,
                    "bbox": {
                        "x0": min(xs),
                        "y0": min(ys),
                        "x1": max(xs),
                        "y1": max(ys)
                    },
                    "source_type": "ocr_text"
                }).execute()

        # -----------------------
        # TABLE EXTRACTION
        # -----------------------

        tables = plumber_page.extract_tables()

        for table in tables:
            if not table:
                continue
            cleaned_table = clean_table_json(table)
            markdown = clean_text(table_to_markdown(cleaned_table))
            bbox_json = {
                "x0": 0,
                "y0": 0,
                "x1": page.rect.width,
                "y1": page.rect.height
            }

            supabase.table("table_blocks").insert({
                "document_id": document_id,
                "page_number": page_number + 1,
                "table_markdown": markdown,
                "table_json": cleaned_table,
                "bbox": bbox_json
            }).execute()

    # 5️⃣ Update status
    supabase.table("documents").update({
        "status": "parsed"
    }).eq("id", document_id).execute()

    print("Parsing completed:", document_id)
