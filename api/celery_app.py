from celery import Celery

# broker="redis://<WSL_IP>:6379/0"
# 172.19.108.1
broker = ("redis://localhost:6379/0",)
backend = "redis://localhost:6379/0"

celery = Celery("worker", broker=broker, backend=backend)
celery.conf.task_routes = {"tasks.ingest_document_task": {"queue": "ocr_queue"}}
