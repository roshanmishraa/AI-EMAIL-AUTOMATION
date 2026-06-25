from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# -----------------------------
# BASE
# -----------------------------
Base = declarative_base()

# -----------------------------
# DATABASE URL FIX (IMPORTANT)
# -----------------------------
DATABASE_URL = settings.DATABASE_URL

# If SQLite is used, ensure async driver
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace(
        "sqlite:///",
        "sqlite+aiosqlite:///"
    )

# -----------------------------
# ENGINE
# -----------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
)

# -----------------------------
# SESSION
# -----------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# -----------------------------
# DEPENDENCY (FOR FASTAPI)
# -----------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session