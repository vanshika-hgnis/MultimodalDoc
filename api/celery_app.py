# celery_app.py
from celery import Celery

celery = Celery("worker")

celery.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0"
)

celery.conf.imports = ("tasks",)