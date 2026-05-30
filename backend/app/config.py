import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve paths relative to the backend directory (where this file lives)
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    STATEMENTS_FOLDER: str = str(BASE_DIR / "statements_inbox")
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'spend_analytics.db'}"


settings = Settings()
