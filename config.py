import os
from secrets import token_hex

# Directorio raíz del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DEV_PATH = os.path.join(BASE_DIR, "src", "database", "dev.db")


class Config:
    SECRET_KEY = (os.environ.get("SECRET_KEY") or token_hex(32))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True
    # Usa env var si existe (producción futura con PostgreSQL),
    # si no, SQLite en src/database/dev.db
    SQLALCHEMY_DATABASE_URI = (os.getenv("DATABASE_URL_DEVELOPMENT") or f"sqlite:///{DB_DEV_PATH}")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
