import logging
from flask import url_for
from flask_mail import Message
from src.utils.extensions import mail
from src.services.auth_service import generate_jwt

logger = logging.getLogger(__name__)


def send_verification_email(user):
    token = generate_jwt(
        user.id,
        purpose="email_verification",
        expires_minutes=1440
    )
    link = url_for(
        "auth.verify_email",
        token=token,
        _external=True
    )
    msg = Message(
        subject="Verifica tu cuenta - Verneris",
        recipients=[user.email]
    )
    msg.body = (
        f"Hola {user.username},\n\n"
        f"Verifica tu cuenta haciendo click aqui:\n"
        f"{link}\n\n"
        f"El enlace expira en 24 horas."
    )
    mail.send(msg)


def send_password_reset_email(user):
    token = generate_jwt(
        user.id,
        purpose="password_reset",
        expires_minutes=30,
    )
    link = url_for(
        "auth.reset_password",
        token=token,
        _external=True,
    )
    msg = Message(
        subject="Recuperar contraseña - Presion Ruedas",
        recipients=[user.email],
    )
    msg.body = (
        f"Hola {user.username},\n\n"
        f"Cambia tu contraseña aqui:\n"
        f"{link}\n\n"
        f"El enlace expira en 30 minutos."
    )
    mail.send(msg)
