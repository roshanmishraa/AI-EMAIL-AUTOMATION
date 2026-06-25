from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # -------------------
    # APP
    # -------------------
    APP_ENV: str = "development"

    # -------------------
    # SQLITE (ONLY)
    # -------------------
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_email.db"
    SYNC_DATABASE_URL: str = "sqlite:///./ai_email.db"

    # -------------------
    # REDIS / CELERY
    # -------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # -------------------
    # AI
    # -------------------
    OPENAI_API_KEY: str = ""

    # -------------------
    # GMAIL
    # -------------------
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/oauth2callback"
    GMAIL_TOKEN_PATH: str = "./storage/gmail_token.json"

    # -------------------
    # RAG (FAISS)
    # -------------------
    FAISS_INDEX_PATH: str = "./storage/faiss_index"
    KB_UPLOAD_DIR: str = "./storage/kb_uploads"

    # -------------------
    # NOTIFICATIONS
    # -------------------
    SLACK_WEBHOOK_URL: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
