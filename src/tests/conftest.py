import pytest
from config import TestingConfig
from src import app_creation
from src.utils.extensions import db as _db


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
