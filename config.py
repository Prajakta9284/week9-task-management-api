
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Application security
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-this-secret"
    )

    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "dev-only-change-this-jwt-secret"
    )

    # SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'week9.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT token settings
    JWT_ACCESS_TOKEN_EXPIRES = 1800  # 30 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days

    # Email settings (used by forgot-password functionality)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")
