from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import os
import shutil

from app.core.deps import get_db, verify_api_key
from app.core.config import settings

from app.services.ai.rag import add_document_to_index
from app.models.knowledge_base import KnowledgeBase, KBChunk   # (assumed model)

router = APIRouter(dependencies=[Depends(verify_api_key)])


# -----------------------------
# UPLOAD KB DOCUMENT
# -----------------------------
@router.post("/upload")
async def upload_kb_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # -----------------------------
    # SAVE FILE LOCALLY
    # -----------------------------
    os.makedirs(settings.KB_UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(settings.KB_UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -----------------------------
    # READ CONTENT
    # -----------------------------
    content = ""
    if file.filename.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

    else:
        # for PDF/DOCX → you can later enhance
        content = file.filename  # placeholder safe fallback

    # -----------------------------
    # ADD TO FAISS INDEX
    # -----------------------------
    chunks_added = await add_document_to_index(
        text=content,
        source=file.filename
    )

    # -----------------------------
    # SAVE TO DB
    # -----------------------------
    kb_doc = KnowledgeBase(
        filename=file.filename,
        file_path=file_path,
        chunks=chunks_added
    )

    db.add(kb_doc)
    await db.commit()

    return {
        "message": "KB document uploaded successfully",
        "file": file.filename,
        "chunks_created": chunks_added
    }


# -----------------------------
# LIST KB DOCUMENTS
# -----------------------------
@router.get("/")
async def list_kb_documents(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(KnowledgeBase))
    docs = result.scalars().all()

    return {
        "total": len(docs),
        "documents": docs
    }


# -----------------------------
# DELETE KB DOCUMENT
# -----------------------------
@router.delete("/{kb_id}")
async def delete_kb_document(
    kb_id: int,
    db: AsyncSession = Depends(get_db)
):

    doc = await db.get(KnowledgeBase, kb_id)

    if not doc:
        raise HTTPException(status_code=404, detail="KB document not found")

    # remove file from disk
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # delete DB record
    await db.delete(doc)
    await db.commit()

    return {"message": "KB document deleted successfully"}