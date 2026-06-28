# ============================================================
# FILE:  backend/app/models/email.py
# CHANGE: user_id ForeignKey add kiya — multi-user support ke liye
#         has_attachments + attachment_names already the (unchanged)
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Enum,
    ForeignKey,
    Boolean,
)

from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
import datetime


# -----------------------------
# ENUMS (UNCHANGED)
# -----------------------------

class EmailCategory(str, enum.Enum):
    legal         = "legal"
    billing       = "billing"
    product_issue = "product_issue"
    delivery      = "delivery"
    refund        = "refund"
    general       = "general"
    spam          = "spam"
    feedback      = "feedback"


class EmailSentiment(str, enum.Enum):
    angry      = "angry"
    frustrated = "frustrated"
    neutral    = "neutral"
    happy      = "happy"
    sad        = "sad"


class EmailStatus(str, enum.Enum):
    new        = "new"
    processing = "processing"
    processed  = "processed"
    replied    = "replied"
    escalated  = "escalated"


# -----------------------------
# EMAIL TABLE
# -----------------------------

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    gmail_message_id = Column(String, unique=True, index=True)
    thread_id        = Column(String, index=True)

    sender  = Column(String)
    subject = Column(String)
    body    = Column(Text)

    received_at = Column(DateTime, default=datetime.datetime.utcnow)

    # ── AI generated fields (UNCHANGED) ──────────────────────
    category         = Column(Enum(EmailCategory), nullable=True)
    sentiment        = Column(Enum(EmailSentiment), nullable=True)
    intent           = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    status           = Column(Enum(EmailStatus), default=EmailStatus.new)

    # ── Attachment fields (UNCHANGED) ────────────────────────
    has_attachments  = Column(Boolean, default=False, nullable=False)
    attachment_names = Column(Text, default="[]", nullable=True)

    # ── NEW: Multi-user — kaun sa user ka email hai ye ───────
    # nullable=True rakha hai taaki purane emails (bina user ke) break na ho
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # ── Relationships ─────────────────────────────────────────
    replies     = relationship("EmailReply", back_populates="email")
    escalations = relationship("Escalation", back_populates="email")
    user        = relationship("User", back_populates="emails")   # ← NEW
