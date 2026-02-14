import fitz  # PyMuPDF
from supabase_client import supabase
import requests
import os
import tempfile


def ingest_document(document_id: str):

    # 1. Fetch document metadata
    doc_response = (
        supabase.table("documents").select("*").eq("id", document_id).execute()
    )

    if not doc_response.data:
        raise Exception("Document not found")

    doc = doc_response.data[0]
    storage_path = doc["storage_path"]

    # 2. Download file from Supabase storage
    response = supabase.storage.from_("documents").download(storage_path)
    if not response:
        raise Exception("Failed to download file from storage")
    file_bytes = response

    # 3. Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    # 4. Open PDF
    pdf = fitz.open(tmp_path)

    for page_number in range(len(pdf)):
        page = pdf[page_number]

        blocks = page.get_text("blocks")

    for block in blocks:
        x0 = block[0]
        y0 = block[1]
        x1 = block[2]
        y1 = block[3]
        text = block[4]

        if text and text.strip():
            supabase.table("text_blocks").insert(
                {
                    "document_id": document_id,
                    "page_number": page_number + 1,
                    "text": text,
                    "bbox": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
                }
            ).execute()

            if text.strip():
                supabase.table("text_blocks").insert(
                    {
                        "document_id": document_id,
                        "page_number": page_number + 1,
                        "text": text,
                        "bbox": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
                    }
                ).execute()

    # 5. Update document status
    supabase.table("documents").update({"status": "parsed"}).eq(
        "id", document_id
    ).execute()
