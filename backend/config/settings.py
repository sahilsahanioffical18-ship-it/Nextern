"""
config/settings.py
Centralized configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = False

    # Database — auto-selects path per environment
    @staticmethod
    def get_db_path() -> str:
        if os.environ.get("VERCEL"):
            return "/tmp/interview_prep.db"
        if os.environ.get("RENDER"):
            return os.path.join(os.path.expanduser("~"), "interview_prep.db")
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "interview_prep.db",
        )

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    # Gemini AI
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    # Public URL (used for OAuth redirect)
    PUBLIC_URL: str = os.environ.get("PUBLIC_URL", "http://localhost:8081")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config() -> Config:
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
