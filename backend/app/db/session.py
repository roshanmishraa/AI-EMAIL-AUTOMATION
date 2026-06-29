from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# ──────────────────────────────────────────
# ASYNC ENGINE — FastAPI ke liye (asyncpg)
# ──────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,          # postgresql+asyncpg://
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"timeout": 10},   # ← Railway hang fix
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ──────────────────────────────────────────
# SYNC ENGINE — Celery tasks ke liye (psycopg2)
# asyncpg Windows pe Celery ke saath event loop crash karta hai
# psycopg2 sync driver is problem se free hai
# ──────────────────────────────────────────
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,     # postgresql://  (psycopg2)
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 10},  # ← psycopg2 ke liye alag param
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
)