# tasks.py

from celery_app import celery
from ingestion import ingest_document

@celery.task
def ingest_document_task(document_id: str):
    print("TASK RECEIVED:", document_id)
    ingest_document(document_id)
