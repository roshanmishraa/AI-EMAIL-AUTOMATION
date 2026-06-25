# Celery task: run full AI pipeline on an email — Day 2
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=2)
def process_email_ai(self, email_id: int):
    """
    Pipeline:
    1. preprocessor.clean_email_body()
    2. classifier.classify_email()
    3. sentiment.detect_sentiment()
    4. reply_generator.generate_reply()   ← includes RAG
    5. escalation_service.check_escalation()
    6. Save results to DB
    7. If escalation → notification_service.send_slack_alert()
    """
    try:
        # TODO: implement (Day 2)
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=15)
