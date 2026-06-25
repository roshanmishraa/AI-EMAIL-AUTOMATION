from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String)
    source_type = Column(String)   # pdf / docx / text
    file_path   = Column(String)
    created_at  = Column(DateTime(timezone=True))

    chunks      = relationship("KBChunk", back_populates="kb_doc", cascade="all, delete")


class KBChunk(Base):
    __tablename__ = "kb_chunks"

    id           = Column(Integer, primary_key=True, index=True)
    kb_id        = Column(Integer, ForeignKey("knowledge_base.id"))
    chunk_text   = Column(Text)
    category_tag = Column(String, nullable=True)
    chunk_index  = Column(Integer)

    kb_doc       = relationship("KnowledgeBase", back_populates="chunks")
