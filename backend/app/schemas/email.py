from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.email import EmailCategory, EmailSentiment, EmailStatus


class EmailOut(BaseModel):
    id: int
    gmail_message_id: str
    sender: str
    subject: str
    body: str
    received_at: datetime

    category: Optional[EmailCategory] = None
    sentiment: Optional[EmailSentiment] = None

    # FIX: make intent safe for API
    intent: Optional[dict] = None

    confidence_score: Optional[float] = None
    status: EmailStatus

    class Config:
        from_attributes = True


class EmailListOut(BaseModel):
    emails: list[EmailOut]
    total: int
