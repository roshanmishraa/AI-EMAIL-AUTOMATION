from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    String
)

from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
import datetime


# -----------------------------
# ENUM
# -----------------------------
class ReplySource(str, enum.Enum):
    ai = "ai"
    human = "human"


# -----------------------------
# REPLY TABLE
# -----------------------------
class EmailReply(Base):
    __tablename__ = "email_replies"

    id = Column(Integer, primary_key=True, index=True)

    # FK → emails table
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)

    generated_by = Column(
        Enum(ReplySource),
        default=ReplySource.ai
    )

    reply_text = Column(Text)

    tone_used = Column(String, nullable=True)

    confidence_score = Column(Float, nullable=True)

    is_approved = Column(Boolean, default=False)

    sent_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    # relationship
    email = relationship("Email", back_populates="replies")
