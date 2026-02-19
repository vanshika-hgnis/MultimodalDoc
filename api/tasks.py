from celery_app import celery
from ingestion import ingest_document


@celery.task(name="tasks.ingest_document_task")
def ingest_document_task(document_id: str):
    ingest_document(document_id)
