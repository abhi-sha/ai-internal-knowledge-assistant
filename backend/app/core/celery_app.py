from celery import Celery
from app.core.config import REDIS_BACKEND_URL,REDIS_BROKER_URL

celery_app=Celery(
    "worker",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone='UTC',
    enable_utc=True
)

import app.tasks.document_ingestion 
# celery_app.autodiscover_tasks(["app.tasks"])