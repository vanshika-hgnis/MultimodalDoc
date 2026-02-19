import fitz
from supabase_client import supabase
import easyocr
from io import BytesIO

# create a single reader (expensive init)
ocr_reader = easyocr.Reader(["en"], gpu=False)


def ingest_document(document_id: str):

    doc_response = (
        supabase.table("documents").select("*").eq("id", document_id).execute()
    )
    if not doc_response.data:
        raise Exception("Document not found")

    storage_path = doc_response.data[0]["storage_path"]
    response = supabase.storage.from_("documents").download(storage_path)

    if not response:
        raise Exception("Failed to download from storage")

    # write local temp file
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response)
        tmp_path = tmp.name

    pdf = fitz.open(tmp_path)

    for page_number in range(len(pdf)):
        page = pdf[page_number]
        blocks = page.get_text("blocks")

        # check if page has text
        page_text_content = " ".join([b[4] for b in blocks if b[4].strip()])

        if page_text_content.strip():
            # use regular PDF text
            for block in blocks:
                x0, y0, x1, y1 = block[:4]
                text = block[4]
                if text.strip():
                    supabase.table("text_blocks").insert(
                        {
                            "document_id": document_id,
                            "page_number": page_number + 1,
                            "text": text,
                            "bbox": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
                            "source_type": "pdf_text",
                        }
                    ).execute()
        else:
            # OCR fallback for scanned page
            # render page to image
            pix = page.get_pixmap(dpi=300)
            image_bytes = pix.tobytes("png")

            # OCR using easyocr
            results = ocr_reader.readtext(image_bytes)

            # combine OCR result words into line text
            for bbox, text, prob in results:
                if not text.strip():
                    continue

                # bbox is list of points [[x1,y1],[x2,y2],...]
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                bbox_json = {
                    "x0": min(xs),
                    "y0": min(ys),
                    "x1": max(xs),
                    "y1": max(ys),
                }

                supabase.table("text_blocks").insert(
                    {
                        "document_id": document_id,
                        "page_number": page_number + 1,
                        "text": text,
                        "bbox": bbox_json,
                        "source_type": "ocr_text",
                    }
                ).execute()

    # update document status at end
    supabase.table("documents").update({"status": "parsed"}).eq(
        "id", document_id
    ).execute()
