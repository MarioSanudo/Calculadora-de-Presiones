import logging
import resend
from flask import url_for, current_app
from flask_mail import Message
from src.utils.extensions import mail
from src.services.auth_service import generate_jwt

logger = logging.getLogger(__name__)

SENDER = "noreply@verneris.es"


def _send_via_resend(to, subject, body):
    """Envía por API HTTP de Resend (producción)."""
    resend.Emails.send({
        "from": SENDER,
        "to": [to],
        "subject": subject,
        "text": body,
    })


def _send_via_smtp(to, subject, body):
    """Envía por SMTP con Flask-Mail (desarrollo con Mailtrap)."""
    msg = Message(subject=subject, recipients=[to])
    msg.body = body
    mail.send(msg)


def _send_email(to, subject, body):
    if current_app.config.get("USE_RESEND_API"):
        _send_via_resend(to, subject, body)
    else:
        _send_via_smtp(to, subject, body)


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
    subject = "Verifica tu cuenta - Verneris"
    body = (
        f"Hola {user.username},\n\n"
        f"Verifica tu cuenta haciendo click aqui:\n"
        f"{link}\n\n"
        f"El enlace expira en 24 horas."
    )
    _send_email(user.email, subject, body)


def send_password_reset_email(user):
    token = generate_jwt(
        user.id,
        purpose="password_reset",
        expires_minutes=30
    )
    link = url_for(
        "auth.reset_password",
        token=token,
        _external=True
    )
    subject = "Recuperar contraseña - Verneris"
    body = (
        f"Hola {user.username},\n\n"
        f"Cambia tu contraseña aqui:\n"
        f"{link}\n\n"
        f"El enlace expira en 30 minutos."
    )
    _send_email(user.email, subject, body)
