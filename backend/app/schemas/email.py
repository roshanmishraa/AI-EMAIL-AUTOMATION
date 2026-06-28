# ============================================================
# FILE:  backend/app/schemas/email.py
# CHANGE: EmailOut mein has_attachments aur attachment_names add kiye
# ============================================================

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReplyOut(BaseModel):
    id:               int
    email_id:         int
    generated_by:     str
    reply_text:       str
    tone_used:        Optional[str]
    confidence_score: Optional[float]
    is_approved:      bool
    sent_at:          Optional[datetime]
    created_at:       datetime

    class Config:
        from_attributes = True


class EmailOut(BaseModel):
    id:               int
    gmail_message_id: str
    thread_id:        Optional[str]
    sender:           Optional[str]
    subject:          Optional[str]
    body:             Optional[str]
    received_at:      datetime
    category:         Optional[str]
    sentiment:        Optional[str]
    intent:           Optional[str]
    confidence_score: Optional[float]
    status:           str

    # ── NEW: attachment fields ──────────────────────────────
    has_attachments:  bool = False
    attachment_names: Optional[str] = "[]"   # JSON string: '["file1.pdf","file2.jpg"]'

    replies: List[ReplyOut] = []

    class Config:
        from_attributes = True


class EmailListOut(BaseModel):
    emails: List[EmailOut]
    total:  int