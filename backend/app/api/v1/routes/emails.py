from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
import json

from app.core.deps import get_db, verify_api_key
from app.models.email import Email, EmailStatus
from app.models.reply import EmailReply
from app.models.thread import EmailThread
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.user import User

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
async def get_thread(
    gmail_thread_id: str,
    user_id: int = Query(..., description="Logged-in user ka ID — sirf unki hi thread aaye"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Email)
        .options(
            selectinload(Email.replies),
            selectinload(Email.escalations),  # ← FIXED
        )
        .where(Email.thread_id == gmail_thread_id)
        .where(Email.user_id == user_id)   # ← NEW: multi-user isolation
        .order_by(Email.received_at.asc())
    )
    emails = result.scalars().all()
    return {"emails": emails, "total": len(emails)}


# ──────────────────────────────────────────
# LIST EMAILS  (with replies + escalations eagerly loaded)
# ──────────────────────────────────────────
@router.get("/", response_model=EmailListOut)
async def list_emails(
    db:        AsyncSession = Depends(get_db),
    user_id:   int = Query(..., description="Logged-in user ka ID — sirf unke hi emails aaye"),
    status:    str = Query(None),
    category:  str = Query(None),
    sentiment: str = Query(None),
    skip:      int = 0,
    limit:     int = 50,
):
    query = (
        select(Email)
        .options(
            selectinload(Email.replies),
            selectinload(Email.escalations),  # ← FIXED
        )
        .where(Email.user_id == user_id)   # ← NEW: ye hi root-cause fix hai
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
# GET SINGLE EMAIL (with replies + escalations)
# ──────────────────────────────────────────
@router.get("/{email_id}", response_model=EmailOut)
async def get_email(
    email_id: int,
    user_id: int = Query(..., description="Ownership check ke liye"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Email)
        .options(
            selectinload(Email.replies),
            selectinload(Email.escalations),  # ← FIXED
        )
        .where(Email.id == email_id)
        .where(Email.user_id == user_id)   # ← NEW: koi aur user ki email na khol sake
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
    user_id: int = Query(..., description="Ownership check ke liye"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Email)
        .options(
            selectinload(Email.replies),
            selectinload(Email.escalations),  # ← FIXED
        )
        .where(Email.id == email_id)
        .where(Email.user_id == user_id)   # ← NEW: ownership check
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

    # FIX: email ke owner ka apna Gmail token fetch karo —
    # pehle ye missing tha, isliye legacy single-file token pe
    # fallback ho raha tha (multi-user mein galat/fail ho jaata)
    user_token = None
    if email.user_id:
        owner = await db.get(User, email.user_id)
        if owner and owner.gmail_token:
            user_token = json.loads(owner.gmail_token)

    # Attempt Gmail send
    sent = False
    try:
        from app.services.gmail_service import send_reply as gmail_send
        sent = gmail_send(
            thread_id=email.thread_id or "",
            to=email.sender or "",
            subject=email.subject or "",
            body=reply.reply_text,
            user_token=user_token,   # ← correct user ka token use hoga
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
# ESCALATE EMAIL (manual — agent khud decide karta hai)
# ──────────────────────────────────────────
@router.post("/{email_id}/escalate")
async def escalate_email(
    email_id: int,
    user_id: int = Query(..., description="Ownership check ke liye"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Email)
        .where(Email.id == email_id)
        .where(Email.user_id == user_id)   # ← NEW: ownership check
    )
    email = result.scalar_one_or_none()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    email.status = EmailStatus.escalated

    # NEW: Escalation table mein bhi row banao (pehle sirf email.status
    # set hota tha, isliye manual escalations track/resolve nahi ho pati thi)
    new_escalation = Escalation(
        email_id=email_id,
        reason=EscalationReason.manual_review,
        status=EscalationStatus.open,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(new_escalation)

    await db.commit()

    return {"message": "Email escalated successfully"}


# ──────────────────────────────────────────
# RESOLVE ESCALATION (human review complete)
# Dono paths (AI-auto escalation + manual escalation) yahan se resolve ho sakte hain
# ──────────────────────────────────────────
@router.post("/{email_id}/resolve-escalation")
async def resolve_escalation(
    email_id: int,
    user_id: int = Query(..., description="Ownership check ke liye"),
    notes: str = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Escalation)
        .join(Email, Escalation.email_id == Email.id)
        .where(Escalation.email_id == email_id)
        .where(Email.user_id == user_id)   # ← NEW: ownership check
        .order_by(Escalation.id.desc())
    )
    escalation = result.scalars().first()

    if not escalation:
        raise HTTPException(
            status_code=404,
            detail="No escalation record found for this email",
        )

    escalation.status      = EscalationStatus.resolved
    escalation.resolved_at = datetime.datetime.utcnow()
    if notes:
        escalation.notes = notes

    await db.commit()

    return {
        "message":     "Escalation marked as resolved",
        "email_id":    email_id,
        "resolved_at": escalation.resolved_at,
    }


# ──────────────────────────────────────────
# RUN AI PIPELINE ON EXISTING EMAIL (manual)
# ──────────────────────────────────────────
@router.post("/{email_id}/process")
async def process_email(
    email_id: int,
    user_id: int = Query(..., description="Ownership check ke liye"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Email)
        .where(Email.id == email_id)
        .where(Email.user_id == user_id)   # ← NEW: ownership check
    )
    email = result.scalar_one_or_none()
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