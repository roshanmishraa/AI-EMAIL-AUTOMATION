# ============================================================
# FILE:  backend/app/core/config.py
# CHANGE: Default DATABASE URLs SQLite se PostgreSQL kar diye
#         Actual values .env se override hongi
# ============================================================

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ──────────────────────────────────────────
    # APP
    # ──────────────────────────────────────────
    APP_ENV: str = "development"
    API_KEY: str = "supersecret-change-me"

    # ──────────────────────────────────────────
    # DATABASE
    # Default values PostgreSQL — .env se override hoga
    # ──────────────────────────────────────────
    DATABASE_URL:      str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_email_db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_email_db"

    # ──────────────────────────────────────────
    # REDIS / CELERY
    # ──────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ──────────────────────────────────────────
    # AI
    # ──────────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ──────────────────────────────────────────
    # GMAIL
    # ──────────────────────────────────────────
    GMAIL_CLIENT_ID:     str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI:  str = "http://localhost:8000/oauth2callback"
    GMAIL_TOKEN_PATH:    str = "./storage/gmail_token.json"

    # ──────────────────────────────────────────
    # RAG
    # ──────────────────────────────────────────
    FAISS_INDEX_PATH: str = "./storage/faiss_index"
    KB_UPLOAD_DIR:    str = "./storage/kb_uploads"

    # ──────────────────────────────────────────
    # SLACK
    # ──────────────────────────────────────────
    SLACK_WEBHOOK_URL: str = ""

    # FRONTEND URL
    FRONTEND_URL: str = "http://localhost:5173"

    # ──────────────────────────────────────────
    # Email Ping / SMTP settings
    # ──────────────────────────────────────────
    AGENT_EMAIL: str = ""
    SMTP_HOST:   str = "smtp.gmail.com"
    SMTP_PORT:   int = 587
    SMTP_USER:   str = ""
    SMTP_PASS:   str = ""

    class Config:
        env_file = ".env"
        extra    = "ignore"


settings = Settings()