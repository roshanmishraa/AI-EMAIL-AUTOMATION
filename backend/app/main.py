from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import json

from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.core.deps import get_db

# CRITICAL: import all models before create_all so their tables are registered
import app.models  # noqa: F401 — side-effect import registers all SQLAlchemy models

from app.api.v1 import router as api_router
from app.services.ai.rag import load_index
from app.services.gmail_service import (
    get_auth_url,
    exchange_code_for_token,
    get_user_email_from_token,
)
from app.models.user import User


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all database tables (User table bhi ab yahan banega)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✓ Database tables created/verified")

    # Load FAISS index from disk into memory
    try:
        load_index()
        logger.info("✓ FAISS RAG index loaded")
    except Exception as e:
        logger.warning(f"FAISS index load warning (non-fatal): {e}")

    yield

    await engine.dispose()
    logger.info("Database connection closed")


app = FastAPI(
    title="AI Email Automation",
    description="Auto-triage, smart reply, sentiment detection & escalation",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # local dev
        settings.FRONTEND_URL,             # production frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")


# ──────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# ──────────────────────────────────────────
# OAUTH ROUTES (no API key needed — ye public endpoints hain)
# ──────────────────────────────────────────

@app.get("/auth/gmail")
async def gmail_auth():
    """
    Step 1: Frontend is URL pe user ko redirect karta hai.
    Google login page khulti hai.
    """
    auth_url = get_auth_url()
    return {"auth_url": auth_url}


@app.get("/oauth2callback")
async def oauth_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Step 2: Google yahan callback karta hai authorization code ke saath.
    - Code → token exchange karo
    - User ki Gmail address nikalo
    - DB mein user save/update karo
    - Frontend pe redirect karo with user email
    """
    try:
        # Code → token exchange
        token_data = exchange_code_for_token(code)

        # Token se Gmail address nikalo
        user_email = get_user_email_from_token(token_data)

        # DB mein check karo — user pehle se hai?
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()

        if user:
            # Existing user — token update karo (refresh ho sakta hai)
            user.gmail_token = json.dumps(token_data)
            import datetime
            user.last_seen = datetime.datetime.utcnow()
        else:
            # Naya user — create karo
            user = User(
                email=user_email,
                gmail_token=json.dumps(token_data),
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        logger.info(f"✓ OAuth success for user: {user_email}")

        # Frontend pe redirect karo — email query param mein bhejo
        # Frontend is email ko store karke API calls mein use karega
        # FIX: /login? pe redirect karo, root / pe nahi —
        # kyunki root route ProtectedRoute hai aur unauthenticated user ko
        # /login pe bhej deta hai jisse query params (auth=success&...) drop ho jaate the
        frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/login?auth=success&email={user_email}&user_id={user.id}"
        )

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/login?auth=error&reason=oauth_failed"
        )


@app.get("/auth/me")
async def get_current_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Frontend user_id se current user info fetch karta hai.
    Ye check karne ke liye ki user logged in hai ya nahi.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user   = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id":         user.id,
        "email":      user.email,
        "is_active":  user.is_active,
        "created_at": user.created_at,
        "last_seen":  user.last_seen,
    }