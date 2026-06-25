from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class KBDocOut(BaseModel):
    id: int
    title: str
    source_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class KBChunkOut(BaseModel):
    id: int
    chunk_text: str
    category_tag: Optional[str]
    chunk_index: int

    class Config:
        from_attributes = True
