# celery_app.py
import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "worker",
    broker=broker_url,
    backend=result_backend
)

celery.conf.imports = ("tasks",)