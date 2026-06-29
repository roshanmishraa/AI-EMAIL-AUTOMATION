from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================================
    # Load Environment Variables
    # ==========================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ==========================================================
    # APP
    # ==========================================================
    APP_ENV: str = "production"
    API_KEY: str = "supersecret-change-me"

    # ==========================================================
    # AI
    # ==========================================================
    OPENAI_API_KEY: str = ""

    # ==========================================================
    # GMAIL
    # ==========================================================
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    # GMAIL_REDIRECT_URI: str = "http://localhost:8000/oauth2callback"
    GMAIL_TOKEN_PATH: str = "./storage/gmail_token.json"

    # 
    REDIS_URL: str = "redis://localhost:6379/0"
    # ==========================================================
    # RAG / VECTOR STORE
    # ==========================================================
    FAISS_INDEX_PATH: str = "./storage/faiss_index"
    KB_UPLOAD_DIR: str = "./storage/kb_uploads"

    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "ai-email-automation"

    # ==========================================================
    # SLACK
    # ==========================================================
    SLACK_WEBHOOK_URL: str = ""

    # ==========================================================
    # FRONTEND
    # ==========================================================
    # FRONTEND_URL: str = "http://localhost:5173"
     

    # ==========================================================
    # EMAIL / SMTP
    # ==========================================================
    AGENT_EMAIL: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""


settings = Settings()