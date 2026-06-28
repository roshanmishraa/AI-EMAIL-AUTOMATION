# ============================================================
# FILE:  backend/app/api/v1/routes/kb.py
# CHANGE: GET /kb/preview?email_id=X endpoint add kiya
#         (sab kuch same, sirf naya route add hua end mein)
# ============================================================

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import os
import shutil
import datetime

from app.core.deps import get_db, verify_api_key
from app.core.config import settings

from app.services.ai.rag import add_document_to_index, retrieve_relevant_chunks
from app.models.knowledge_base import KnowledgeBase, KBChunk
from app.models.email import Email                        # ← NEW

router = APIRouter(dependencies=[Depends(verify_api_key)])


# ──────────────────────────────────────────
# TEXT EXTRACTION HELPERS (UNCHANGED)
# ──────────────────────────────────────────
def _extract_text_from_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages  = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as e:
        print(f"[KB] PDF extraction failed: {e}")
        return ""


def _extract_text_from_docx(path: str) -> str:
    try:
        from docx import Document
        doc   = Document(path)
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paras).strip()
    except Exception as e:
        print(f"[KB] DOCX extraction failed: {e}")
        return ""


def _read_file_content(file_path: str, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "pdf":
        return _extract_text_from_pdf(file_path)
    elif ext == "docx":
        return _extract_text_from_docx(file_path)
    elif ext in ("txt", "md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""


# ──────────────────────────────────────────
# UPLOAD KB DOCUMENT (UNCHANGED)
# ──────────────────────────────────────────
@router.post("/upload")
async def upload_kb_document(
    file: UploadFile = File(...),
    category_tag: str = Form(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    os.makedirs(settings.KB_UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.KB_UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content = _read_file_content(file_path, file.filename)

    if not content.strip():
        print(f"[KB] Warning: no text extracted from {file.filename}")
        content = f"[No text extracted from {file.filename}]"

    chunks_added = await add_document_to_index(
        text=content,
        source=file.filename,
        category_tag=category_tag,
    )

    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else "txt"

    kb_doc = KnowledgeBase(
        title=file.filename,
        source_type=ext,
        file_path=file_path,
        chunk_count=chunks_added,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(kb_doc)
    await db.commit()
    await db.refresh(kb_doc)

    return {
        "message":        "KB document uploaded and indexed successfully",
        "id":             kb_doc.id,
        "file":           file.filename,
        "source_type":    ext,
        "category_tag":   category_tag,
        "chunks_created": chunks_added,
    }


# ──────────────────────────────────────────
# LIST KB DOCUMENTS (UNCHANGED)
# ──────────────────────────────────────────
@router.get("/")
async def list_kb_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(KnowledgeBase).order_by(KnowledgeBase.created_at.desc())
    )
    docs = result.scalars().all()

    return {
        "total": len(docs),
        "documents": [
            {
                "id":          d.id,
                "title":       d.title,
                "source_type": d.source_type,
                "chunk_count": d.chunk_count,
                "created_at":  d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ],
    }


# ──────────────────────────────────────────
# DELETE KB DOCUMENT (UNCHANGED)
# ──────────────────────────────────────────
@router.delete("/{kb_id}")
async def delete_kb_document(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
):
    doc = await db.get(KnowledgeBase, kb_id)
    if not doc:
        raise HTTPException(status_code=404, detail="KB document not found")

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    await db.commit()

    return {"message": f"KB document '{doc.title}' deleted successfully"}


# ──────────────────────────────────────────
# NEW: CHUNK PREVIEW FOR A SPECIFIC EMAIL
# GET /kb/preview?email_id=42
# Returns which KB chunks would be used to generate reply for this email
# ──────────────────────────────────────────
@router.get("/preview")
async def preview_chunks_for_email(
    email_id: int = Query(..., description="ID of the email to preview chunks for"),
    db: AsyncSession = Depends(get_db),
):
    """
    Simulates the RAG retrieval that would happen when generating
    a reply for the given email. Returns the top KB chunks.
    """
    # Fetch the email
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    body     = email.body or ""
    category = email.category.value if email.category else None

    # Run the same retrieval the reply generator would use
    chunks = await retrieve_relevant_chunks(
        query=body,
        category=category,
        top_k=5,
    )

    return {
        "email_id":       email_id,
        "email_subject":  email.subject or "(no subject)",
        "category":       category,
        "chunks_found":   len(chunks),
        "chunks":         chunks,
    }