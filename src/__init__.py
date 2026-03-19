from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask
from .utils.extensions import (db, migrate, login_manager, bcrypt, csrf, limiter)
from config import DevelopmentConfig
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def app_creation(config_class=None):

    sentry_sdk.init(
        dsn="https://b480bef0fbff32420ffeaaf8563a3757@o4510783416762368.ingest.de.sentry.io/4511066566361168",
        integrations=[FlaskIntegration()],  traces_sample_rate=0.2
    )

    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class or DevelopmentConfig)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Login config
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesion primero."  #En rutas protegidas por login_requiered
    login_manager.login_message_category = "info"

    # User loader
    from src.models.user import User

    @login_manager.user_loader
    def load_user(user_id):  # user_id es el UUID del alternative_id
        return User.query.filter_by(alternative_id=user_id).first()

    # Blueprints
    from src.routes.auth import auth_bp
    from src.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
