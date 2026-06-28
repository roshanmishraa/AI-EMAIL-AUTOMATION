# ============================================================
# FILE:  backend/app/api/v1/__init__.py
# CHANGE: notifications router add kiya (1 line add, rest same)
# ============================================================

from fastapi import APIRouter
from app.api.v1.routes import (
    emails,
    kb,
    analytics,
    settings as settings_router,
    notifications,        # ← NEW
)

router = APIRouter()
router.include_router(emails.router,          prefix="/emails",        tags=["emails"])
router.include_router(kb.router,              prefix="/kb",            tags=["knowledge-base"])
router.include_router(analytics.router,       prefix="/analytics",     tags=["analytics"])
router.include_router(settings_router.router, prefix="/settings",      tags=["settings"])
router.include_router(notifications.router,   prefix="/notifications", tags=["notifications"])  # ← NEW
