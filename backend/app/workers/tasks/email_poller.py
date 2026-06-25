# Celery task: fetch new emails every 60s — Day 1
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def fetch_new_emails_task(self):
    """
    1. Call gmail_service.fetch_unread_emails()
    2. Save raw emails to DB
    3. Dispatch ai_processor task for each new email
    """
    try:
        # TODO: implement
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
