from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import json
import asyncio

from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.core.deps import get_db

import app.models  # noqa: F401
import os
from app.api.v1 import router as api_router
from app.services.ai.rag import load_index
from app.services.gmail_service import (
    get_auth_url,
    exchange_code_for_token,
    get_user_email_from_token,
)
from app.models.user import User


logger = logging.getLogger(__name__)


async def init_db():
    """DB tables background mein banao — startup block nahi karega"""
    try:
        async with engine.begin() as conn:
            await asyncio.wait_for(
                conn.run_sync(Base.metadata.create_all),
                timeout=30.0,
            )
        logger.info("✓ Database tables created/verified")
    except asyncio.TimeoutError:
        logger.error("❌ DB connection timeout — DATABASE_URL check karo")
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB ko background task mein run karo — uvicorn ko block nahi karega
    asyncio.create_task(init_db())
    logger.info("✓ DB init task scheduled")

    # FAISS index
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
        "http://localhost:5173",
        os.getenv("FRONTEND_URL"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/auth/gmail")
async def gmail_auth():
    auth_url = get_auth_url()
    print("auth_url ::::", auth_url)
    return {"auth_url": auth_url}


@app.get("/oauth2callback")
async def oauth_callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        token_data = exchange_code_for_token(code)
        user_email = get_user_email_from_token(token_data)

        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()

        if user:
            user.gmail_token = json.dumps(token_data)
            import datetime
            user.last_seen = datetime.datetime.utcnow()
        else:
            user = User(
                email=user_email,
                gmail_token=json.dumps(token_data),
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        logger.info(f"✓ OAuth success for user: {user_email}")

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