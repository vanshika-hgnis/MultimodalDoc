# tasks.py

from celery_app import celery
from ingestion import ingest_document
from embedding_service import generate_embedding
from supabase_client import supabase



@celery.task
def ingest_document_task(document_id: str):
    print("TASK RECEIVED:", document_id)
    ingest_document(document_id)

from embedding_service import generate_embedding
from supabase_client import supabase

@celery.task
def embed_document_task(document_id: str):

    # Embed text blocks
    text_blocks = (
        supabase.table("text_blocks")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    ).data

    for block in text_blocks:
        embedding = generate_embedding(block["text"])

        supabase.table("text_blocks").update({
            "embedding": embedding
        }).eq("id", block["id"]).execute()

    # Embed table blocks
    table_blocks = (
        supabase.table("table_blocks")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    ).data

    for block in table_blocks:
        embedding = generate_embedding(block["table_markdown"])

        supabase.table("table_blocks").update({
            "embedding": embedding
        }).eq("id", block["id"]).execute()

    supabase.table("documents").update({
        "status": "embedded"
    }).eq("id", document_id).execute()

    print("Embedding completed:", document_id)
