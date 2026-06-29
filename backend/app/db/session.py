from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# ──────────────────────────────────────────
# DATABASE URL
# Must be postgresql+asyncpg:// in .env
# Example: postgresql+asyncpg://user:password@localhost:5432/dbname
# ──────────────────────────────────────────
DATABASE_URL = settings.DATABASE_URL

# ──────────────────────────────────────────
# ENGINE
# ──────────────────────────────────────────
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    # PostgreSQL pool settings
    pool_size=10,
    max_overflow=20,
)

# ──────────────────────────────────────────
# SESSION FACTORY
# ──────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)