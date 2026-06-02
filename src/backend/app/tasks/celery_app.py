"""Celery application instance (INC-005 hardening)."""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cdf_sigtrace",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.ingestion_tasks",
        "app.tasks.analysis_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,           # only ack after completion — no lost tasks on worker crash
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # fair dispatch for long-running tasks
    task_soft_time_limit=600,      # 10 min soft limit
    task_time_limit=900,           # 15 min hard kill
)
