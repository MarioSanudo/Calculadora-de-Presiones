from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import logging
import os
import resend
from flask import Flask
from .utils.extensions import (
    db, migrate, login_manager,
    bcrypt, csrf, limiter, mail, oauth
)
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s")


def _get_config():
    from config import (
        DevelopmentConfig, ProductionConfig, TestingConfig
    )
    env = os.environ.get("FLASK_ENV", "development")
    return {
        "production": ProductionConfig,
        "testing": TestingConfig,
    }.get(env, DevelopmentConfig)


def app_creation(config_class=None):
    config_class = config_class or _get_config()

    dsn = os.environ.get("DSN")
    if dsn and os.environ.get("FLASK_ENV") == "production":
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration(), LoggingIntegration(
                        level=logging.INFO,        # breadcrumbs desde INFO
                        event_level=logging.ERROR)],  # eventos en Sentry desde ERROR
            traces_sample_rate=1,
            environment="production")

    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    # Inicializar Resend una sola vez si estamos en producción
    if app.config.get("USE_RESEND_API"):
        resend.api_key = app.config["RESEND_API_KEY"]

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    # Google OAuth provider
    oauth.register(
        name="google",
        server_metadata_url=(
            "https://accounts.google.com"       #Creo que es para desarrollo tengo que mirar mejor la separación de config entre producción y desarrollo
            "/.well-known/openid-configuration"
        ),
        client_kwargs={"scope": "openid email profile"})

    # Login config
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión primero."  #En rutas protegidas por login_requiered
    login_manager.login_message_category = "info"

    # User loader
    from src.models.user import User
    from src.models.analysis import Analysis  # para que Flask-Migrate detecte la tabla

    @login_manager.user_loader
    def load_user(user_id):  # user_id es el UUID del alternative_id
        return User.query.filter_by(alternative_id=user_id).first() #Coge el usuario logueado

    # Blueprints
    from src.routes.auth import auth_bp
    from src.routes.main import main_bp
    from src.routes.errors import errors_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)

    # Reverse proxy (Railway / nginx): IP real del cliente para rate limit
    if not app.debug:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1
        )

    @app.after_request
    def security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )
        if not app.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return app
