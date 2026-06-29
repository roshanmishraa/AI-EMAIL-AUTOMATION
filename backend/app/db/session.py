from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import os

# ==========================================================
# Read database URLs from Environment Variables (.env/Railway)
# ==========================================================

DATABASE_URL = os.getenv("DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

if not SYNC_DATABASE_URL:
    raise ValueError("SYNC_DATABASE_URL environment variable is not set.")

# ==========================================================
# Async Engine (FastAPI)
# ==========================================================

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"timeout": 10},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ==========================================================
# Sync Engine (Celery / Background Jobs)
# ==========================================================

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 10},
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
)