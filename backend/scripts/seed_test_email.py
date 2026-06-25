"""
Seed a test email directly into DB (bypass Gmail).
Useful for testing AI pipeline without real Gmail.

Usage:
  cd backend
  python scripts/seed_test_email.py
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.email import Email, EmailStatus


async def seed():
    async with AsyncSessionLocal() as db:
        email = Email(
            gmail_message_id="test-001",
            thread_id="thread-test-001",
            sender="angry.customer@example.com",
            subject="My order never arrived and this is unacceptable!!",
            body="""I placed order #12345 three weeks ago and it still hasn't arrived.
I've contacted support twice with no resolution. This is completely unacceptable.
If I don't hear back within 24 hours I will be forced to take legal action and
dispute this charge with my bank. This is absolutely terrible service.""",
            received_at=datetime.now(timezone.utc),
            status=EmailStatus.new,
        )
        db.add(email)
        await db.commit()
        print(f"Seeded test email with id={email.id}")


if __name__ == "__main__":
    asyncio.run(seed())
