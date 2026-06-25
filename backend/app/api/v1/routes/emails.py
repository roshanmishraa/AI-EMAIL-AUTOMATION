from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, verify_api_key
from app.models.email import Email, EmailStatus
from app.models.reply import EmailReply

from app.schemas.email import EmailOut, EmailListOut

from app.workers.tasks.ai_processor import process_email_ai

router = APIRouter(dependencies=[Depends(verify_api_key)])


# -----------------------------
# LIST EMAILS
# -----------------------------
@router.get("/", response_model=EmailListOut)
async def list_emails(
    db: AsyncSession = Depends(get_db),
    status: str = Query(None),
    category: str = Query(None),
    sentiment: str = Query(None),
    skip: int = 0,
    limit: int = 50,
):

    query = select(Email)

    if status:
        query = query.where(Email.status == status)
    if category:
        query = query.where(Email.category == category)
    if sentiment:
        query = query.where(Email.sentiment == sentiment)

    result = await db.execute(query.offset(skip).limit(limit))
    emails = result.scalars().all()

    return {
        "emails": emails,
        "total": len(emails)
    }


# -----------------------------
# GET SINGLE EMAIL
# -----------------------------
@router.get("/{email_id}", response_model=EmailOut)
async def get_email(email_id: int, db: AsyncSession = Depends(get_db)):

    email = await db.get(Email, email_id)

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return email


# -----------------------------
# APPROVE & SEND REPLY
# -----------------------------
@router.post("/{email_id}/reply")
async def approve_and_send_reply(
    email_id: int,
    db: AsyncSession = Depends(get_db)
):

    email = await db.get(Email, email_id)

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # get latest AI reply
    result = await db.execute(
        select(EmailReply)
        .where(EmailReply.email_id == email_id)
        .order_by(EmailReply.id.desc())
    )

    reply = result.scalars().first()

    if not reply:
        raise HTTPException(status_code=404, detail="No reply found")

    # TODO: integrate Gmail send (later)
    reply.is_approved = True
    email.status = EmailStatus.replied

    await db.commit()

    return {"message": "Reply approved and marked as sent"}


# -----------------------------
# ESCALATE EMAIL
# -----------------------------
@router.post("/{email_id}/escalate")
async def escalate_email(email_id: int, db: AsyncSession = Depends(get_db)):

    email = await db.get(Email, email_id)

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    email.status = EmailStatus.escalated

    await db.commit()

    return {"message": "Email escalated successfully"}


# -----------------------------
# TRIGGER AI PIPELINE
# -----------------------------
@router.post("/trigger-fetch")
async def trigger_email_fetch():

    from app.workers.tasks.email_poller import fetch_new_emails_task

    fetch_new_emails_task.delay()

    return {"message": "fetch triggered"}


# -----------------------------
# RUN AI PIPELINE MANUALLY (IMPORTANT FOR DEMO)
# -----------------------------
@router.post("/{email_id}/process")
async def process_email(email_id: int):

    process_email_ai.delay(email_id)

    return {
        "message": "AI pipeline triggered",
        "email_id": email_id
    }
