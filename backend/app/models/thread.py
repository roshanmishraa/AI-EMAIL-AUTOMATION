from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.db.base import Base
import enum


class ThreadStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    escalated = "escalated"


class EmailThread(Base):
    __tablename__ = "email_threads"

    id              = Column(Integer, primary_key=True, index=True)
    gmail_thread_id = Column(String, unique=True, index=True)
    last_message_at = Column(DateTime(timezone=True))
    status          = Column(Enum(ThreadStatus), default=ThreadStatus.open)
    message_count   = Column(Integer, default=1)
    priority_level  = Column(Integer, default=0)
