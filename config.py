import os
from datetime import timedelta
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
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    WTF_CSRF_TIME_LIMIT = 3600

    # Flask-Mail con Mailtrap si es desarrollo
    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = (
        os.environ.get("MAIL_USE_TLS", "true").lower()
        == "true")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")


    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get(
        "GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get(
        "GOOGLE_CLIENT_SECRET")


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL_DEVELOPMENT")
        or f"sqlite:///{DB_DEV_PATH}"
    )


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

    # Resend — producción, utilizando SMPT como comunicación aunque predomine API ya esta configurado con flask-mail
    MAIL_SERVER = "smtp.resend.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "resend"    
    MAIL_PASSWORD = os.environ.get("RESEND_API_KEY")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "noreply@verneris.es")
    
    # DATABASE_PUBLIC_URL para acceso externo (railway run local)
    # DATABASE_URL para acceso interno (dentro de Railway)
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_PUBLIC_URL")
        or os.getenv("DATABASE_URL")
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    GOOGLE_CLIENT_ID = "test-client-id"
    GOOGLE_CLIENT_SECRET = "test-client-secret"
