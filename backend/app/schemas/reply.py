from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.reply import ReplySource


class ReplyOut(BaseModel):
    id: int
    email_id: int
    generated_by: ReplySource
    reply_text: str
    tone_used: Optional[str]
    confidence_score: Optional[float]
    is_approved: bool
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApproveReplyIn(BaseModel):
    reply_id: int
    edited_text: Optional[str] = None  # if human edited before approving
