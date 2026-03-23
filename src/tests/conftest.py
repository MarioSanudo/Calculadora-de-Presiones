import pytest
from config import TestingConfig
from src import app_creation
from src.utils.extensions import db as _db
from src.models.user import User
from src.services.auth_service import hash_password


@pytest.fixture()
def app():
    app = app_creation(config_class=TestingConfig)

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    with app.app_context():
        yield _db.session


@pytest.fixture()
def verified_user(app, client):
    """Crea un usuario verificado listo para login."""
    _PASS = "Securepass1!"
    with app.app_context():
        user = User(
            username="Verified",
            surname="User",
            email="verified@example.com",
            password_hash=hash_password(_PASS),
            is_verified=True,
        )
        _db.session.add(user)
        _db.session.commit()
    return {
        "email": "verified@example.com",
        "password": _PASS,
    }
