# Test the full AI pipeline on a sample email
import pytest
import asyncio
from app.services.ai.classifier import classify_email
from app.services.ai.sentiment import detect_sentiment
from app.services.ai.reply_generator import generate_reply

SAMPLE_EMAIL = {
    "subject": "My order hasn't arrived after 3 weeks!",
    "body": """I placed order #45678 three weeks ago and it still hasn't come.
I've tried contacting you twice. This is completely unacceptable.
I want a full refund immediately or I'll dispute with my bank.""",
}

@pytest.mark.asyncio
async def test_classification():
    result = await classify_email(**SAMPLE_EMAIL)
    assert result.category in ["delivery", "refund", "general"]
    assert 0 <= result.confidence <= 100

@pytest.mark.asyncio
async def test_sentiment():
    result = await detect_sentiment(SAMPLE_EMAIL["body"])
    assert result.sentiment in ["angry", "frustrated"]
    assert result.urgency_score > 50

@pytest.mark.asyncio
async def test_full_pipeline():
    cls = await classify_email(**SAMPLE_EMAIL)
    snt = await detect_sentiment(SAMPLE_EMAIL["body"])
    rpl = await generate_reply(
        subject=SAMPLE_EMAIL["subject"],
        body=SAMPLE_EMAIL["body"],
        category=cls.category,
        sentiment=snt.sentiment,
    )
    assert len(rpl.draft_reply) > 50
    assert 0 <= rpl.confidence_score <= 100
