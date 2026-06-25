from celery import Celery
from celery.schedules import timedelta
from app.core.config import settings


celery_app = Celery(
    "ai_email_automation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks.email_poller",
        "app.workers.tasks.ai_processor"
    ],
)


# -----------------------------
# BEAT SCHEDULE (IMPROVED)
# -----------------------------
celery_app.conf.beat_schedule = {
    "fetch-emails-every-60s": {
        "task": "app.workers.tasks.email_poller.fetch_new_emails_task",
        "schedule": timedelta(seconds=60),
    },
}


celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True
