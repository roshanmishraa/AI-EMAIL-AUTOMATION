from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# ──────────────────────────────────────────
# DATABASE URL
# ──────────────────────────────────────────
DATABASE_URL = settings.DATABASE_URL

# Ensure correct async driver for SQLite
if DATABASE_URL.startswith("sqlite") and "+aiosqlite" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# ──────────────────────────────────────────
# ENGINE
# ──────────────────────────────────────────
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    # SQLite-specific: avoid "database is locked" in concurrent Celery tasks
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# ──────────────────────────────────────────
# SESSION FACTORY
# ──────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)