from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String)          # filename e.g. "refund_policy.pdf"
    source_type = Column(String)          # "pdf" | "docx" | "txt"
    file_path   = Column(String)
    chunk_count = Column(Integer, default=0)   # how many chunks were created
    created_at  = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    chunks = relationship("KBChunk", back_populates="kb_doc", cascade="all, delete")


class KBChunk(Base):
    __tablename__ = "kb_chunks"

    id            = Column(Integer, primary_key=True, index=True)
    kb_id         = Column(Integer, ForeignKey("knowledge_base.id"))
    chunk_text    = Column(Text)
    category_tag  = Column(String, nullable=True)   # used for filtered RAG retrieval
    chunk_index   = Column(Integer)
    # embedding stored as JSON string in SQLite — in Postgres use VECTOR type
    embedding_json = Column(Text, nullable=True)

    kb_doc = relationship("KnowledgeBase", back_populates="chunks")