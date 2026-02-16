from celery import Celery

# broker="redis://<WSL_IP>:6379/0"
# 172.19.108.1
celery = Celery(
    "worker", broker="redis://172.19.108.1:6379/0", backend="redis://localhost:6379/0"
)

celery.conf.task_routes = {"tasks.ingest_document_task": {"queue": "ocr_queue"}}
