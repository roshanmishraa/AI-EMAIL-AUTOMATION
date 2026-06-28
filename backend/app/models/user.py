# ============================================================
# FILE:  backend/app/models/user.py
# NEW FILE: Multi-user OAuth support ke liye
#           Har user ka Gmail token DB mein store hoga
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)

    # User ki Gmail address — unique identifier
    email      = Column(String, unique=True, index=True, nullable=False)

    # Gmail OAuth token JSON (access_token + refresh_token)
    # Poora token dict yahan store hoga as JSON string
    gmail_token = Column(Text, nullable=True)

    # Kab login kiya pehli baar
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)

    # Kab last baar active tha
    last_seen   = Column(DateTime, default=datetime.datetime.utcnow)

    # Account active hai ya nahi
    is_active   = Column(Boolean, default=True)

    # Relationship: is user ki saari emails
    emails = relationship("Email", back_populates="user")