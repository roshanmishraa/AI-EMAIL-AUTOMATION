from fastapi import Header, HTTPException, status
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal


# ---------------------------
# DATABASE DEPENDENCY
# ---------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------
# API KEY SECURITY
# ---------------------------
async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Simple API key guard.
    Required header:
        X-API-Key: <your_api_key>
    """

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing"
        )

    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
