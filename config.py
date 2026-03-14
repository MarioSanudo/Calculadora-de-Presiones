import os
from secrets import token_hex


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or token_hex(32)
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL_DEVELOPMENT"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
