from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask
from .utils.extensions import (
    db, migrate, login_manager, bcrypt, csrf, limiter
)
from config import DevelopmentConfig


def app_creation():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(DevelopmentConfig)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Login config
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesion primero."
    login_manager.login_message_category = "info"

    # User loader
    from src.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from src.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
