from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, verify_api_key
from app.models.email import Email, EmailStatus
from app.models.reply import EmailReply
from app.models.thread import EmailThread

from app.schemas.email import EmailOut, EmailListOut

from app.workers.tasks.ai_processor import process_email_ai

router = APIRouter(dependencies=[Depends(verify_api_key)])


# ──────────────────────────────────────────
# IMPORTANT: Fixed-path routes MUST come before /{email_id}
# otherwise FastAPI matches "trigger-fetch" as an email_id integer
# ──────────────────────────────────────────

# TRIGGER GMAIL FETCH (manual) — MUST be before /{email_id}
@router.post("/trigger-fetch")
async def trigger_email_fetch():
    from app.workers.tasks.email_poller import fetch_new_emails_task
    fetch_new_emails_task.delay()
    return {"message": "Gmail fetch triggered — check Celery logs"}


# GET THREAD — all emails in a Gmail thread — MUST be before /{email_id}
@router.get("/thread/{gmail_thread_id}", response_model=EmailListOut)
async def get_thread(gmail_thread_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Email)
        .options(selectinload(Email.replies))
        .where(Email.thread_id == gmail_thread_id)
        .order_by(Email.received_at.asc())
    )
    emails = result.scalars().all()
    return {"emails": emails, "total": len(emails)}


# ──────────────────────────────────────────
# LIST EMAILS  (with replies eagerly loaded)
# ──────────────────────────────────────────
@router.get("/", response_model=EmailListOut)
async def list_emails(
    db:        AsyncSession = Depends(get_db),
    status:    str = Query(None),
    category:  str = Query(None),
    sentiment: str = Query(None),
    skip:      int = 0,
    limit:     int = 50,
):
    query = (
        select(Email)
        .options(selectinload(Email.replies))
        .order_by(Email.received_at.desc())
    )

    if status:
        query = query.where(Email.status == status)
    if category:
        query = query.where(Email.category == category)
    if sentiment:
        query = query.where(Email.sentiment == sentiment)

    result = await db.execute(query.offset(skip).limit(limit))
    emails = result.scalars().all()

    return {"emails": emails, "total": len(emails)}


# ──────────────────────────────────────────
# GET SINGLE EMAIL (with replies)
# ──────────────────────────────────────────
@router.get("/{email_id}", response_model=EmailOut)
async def get_email(email_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Email)
        .options(selectinload(Email.replies))
        .where(Email.id == email_id)
    )
    email = result.scalar_one_or_none()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return email


# ──────────────────────────────────────────
# APPROVE & SEND REPLY
# ──────────────────────────────────────────
@router.post("/{email_id}/reply")
async def approve_and_send_reply(
    email_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Email)
        .options(selectinload(Email.replies))
        .where(Email.id == email_id)
    )
    email = result.scalar_one_or_none()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Get the latest AI-generated reply
    reply_result = await db.execute(
        select(EmailReply)
        .where(EmailReply.email_id == email_id)
        .order_by(EmailReply.id.desc())
    )
    reply = reply_result.scalars().first()

    if not reply:
        raise HTTPException(
            status_code=404,
            detail="No AI reply found — run /process first",
        )

    # Attempt Gmail send
    sent = False
    try:
        from app.services.gmail_service import send_reply as gmail_send
        import datetime
        sent = gmail_send(
            thread_id=email.thread_id or "",
            to=email.sender or "",
            subject=email.subject or "",
            body=reply.reply_text,
        )
        if sent:
            reply.sent_at = datetime.datetime.utcnow()
    except Exception as e:
        print(f"[EmailRoute] Gmail send failed (marking approved anyway): {e}")

    # Mark approved regardless (agent reviewed it)
    reply.is_approved = True
    email.status      = EmailStatus.replied

    await db.commit()

    return {
        "message":    "Reply approved" + (" and sent via Gmail" if sent else " (Gmail send failed — check token)"),
        "email_id":   email_id,
        "reply_id":   reply.id,
        "gmail_sent": sent,
    }


# ──────────────────────────────────────────
# ESCALATE EMAIL
# ──────────────────────────────────────────
@router.post("/{email_id}/escalate")
async def escalate_email(email_id: int, db: AsyncSession = Depends(get_db)):
    email = await db.get(Email, email_id)

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    email.status = EmailStatus.escalated
    await db.commit()

    return {"message": "Email escalated successfully"}


# ──────────────────────────────────────────
# RUN AI PIPELINE ON EXISTING EMAIL (manual)
# ──────────────────────────────────────────
@router.post("/{email_id}/process")
async def process_email(email_id: int, db: AsyncSession = Depends(get_db)):
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Reset status so pipeline will re-run
    email.status = EmailStatus.new
    await db.commit()

    process_email_ai.delay(email_id)

    return {
        "message":  "AI pipeline triggered",
        "email_id": email_id,
    }