import os
from secrets import token_hex

# Directorio raíz del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DEV_PATH = os.path.join(BASE_DIR, "src", "database", "dev.db")


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or token_hex(32)
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Flask-Mail
    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER", "localhost"
    )

    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = (
        os.environ.get("MAIL_USE_TLS", "true").lower()
        == "true"
    )
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")


    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get(
        "GOOGLE_CLIENT_ID"
    )
    GOOGLE_CLIENT_SECRET = os.environ.get(
        "GOOGLE_CLIENT_SECRET"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL_DEVELOPMENT")
        or f"sqlite:///{DB_DEV_PATH}"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    GOOGLE_CLIENT_ID = "test-client-id"
    GOOGLE_CLIENT_SECRET = "test-client-secret"
