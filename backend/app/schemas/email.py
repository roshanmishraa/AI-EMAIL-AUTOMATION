from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.email import EmailCategory, EmailSentiment, EmailStatus
from app.models.reply import ReplySource


# ──────────────────────────────────────────
# REPLY NESTED (inline so EmailOut can use it without circular import)
# ──────────────────────────────────────────
class ReplyInline(BaseModel):
    id: int
    generated_by: ReplySource
    reply_text: str
    tone_used: Optional[str] = None
    confidence_score: Optional[float] = None
    is_approved: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# SINGLE EMAIL OUT
# ──────────────────────────────────────────
class EmailOut(BaseModel):
    id: int
    gmail_message_id: str
    thread_id: Optional[str] = None   # Gmail thread ID string
    sender: str
    subject: str
    body: str
    received_at: datetime

    # AI fields — nullable before processing
    category: Optional[EmailCategory] = None
    sentiment: Optional[EmailSentiment] = None
    intent: Optional[str] = None       # stored as TEXT in DB
    confidence_score: Optional[float] = None
    status: EmailStatus

    # Replies — the frontend needs this to show AI draft
    replies: List[ReplyInline] = []

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# LIST RESPONSE
# ──────────────────────────────────────────
class EmailListOut(BaseModel):
    emails: List[EmailOut]
    total: int