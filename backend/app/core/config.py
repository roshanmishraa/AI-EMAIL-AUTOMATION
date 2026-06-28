# ============================================================
# FILE:  backend/app/core/config.py
# CHANGE: AGENT_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_USER,
#         SMTP_PASS settings add kiye for email ping feature
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
    # ──────────────────────────────────────────
    DATABASE_URL:      str = "sqlite+aiosqlite:///./ai_email.db"
    SYNC_DATABASE_URL: str = "sqlite:///./ai_email.db"

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

    # ──────────────────────────────────────────
    # NEW: Email Ping / SMTP settings
    # ──────────────────────────────────────────
    # Who to email when an escalation happens
    AGENT_EMAIL: str = ""

    # SMTP server settings
    # For Gmail: SMTP_HOST=smtp.gmail.com, SMTP_PORT=587
    #            SMTP_USER=your@gmail.com, SMTP_PASS=<app-password>
    # For SendGrid: SMTP_HOST=smtp.sendgrid.net, SMTP_PORT=587
    #               SMTP_USER=apikey, SMTP_PASS=<sendgrid-api-key>
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    class Config:
        env_file = ".env"
        extra    = "ignore"


settings = Settings()