from fastapi import FastAPI, UploadFile, File, HTTPException
from ingestion import ingest_document
from tasks import ingest_document_task
from supabase_client import supabase
import uuid

app = FastAPI()


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        storage_path = f"{file_id}/{file.filename}"

        contents = await file.read()

        # Upload to Supabase Storage
        supabase.storage.from_("documents").upload(
            storage_path, contents, {"content-type": file.content_type}
        )

        # Insert metadata into Postgres
        data = {
            "filename": file.filename,
            "mime_type": file.content_type,
            "size": len(contents),
            "storage_path": storage_path,
            "status": "uploaded",
        }

        response = supabase.table("documents").insert(data).execute()
        print(response)
        return {"document_id": response.data[0]["id"], "message": "Upload successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{document_id}")
def get_document(document_id: str):
    response = supabase.table("documents").select("*").eq("id", document_id).execute()
    return response.data


@app.post("/documents/{document_id}/parse")
def parse_document(document_id: str):

    # mark status processing
    supabase.table("documents").update({"status": "processing"}).eq(
        "id", document_id
    ).execute()

    # trigger async job
    ingest_document_task.delay(document_id)

    return {"message": "Parsing started in background"}
