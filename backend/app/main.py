from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# CRITICAL: import all models before create_all so their tables are registered
import app.models  # noqa: F401 — side-effect import registers all SQLAlchemy models

from app.api.v1 import router as api_router
from app.services.ai.rag import load_index


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all database tables
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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}