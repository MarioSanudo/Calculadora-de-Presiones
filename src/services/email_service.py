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


def _build_action_link(user_id, purpose, expires_minutes, endpoint):
    """Genera token JWT y construye la URL de acción."""
    token = generate_jwt(
        user_id,
        purpose=purpose,
        expires_minutes=expires_minutes
    )
    return url_for(endpoint, token=token, _external=True)


def _build_body(username, action_text, link, expiry_text):
    return (
        f"Hola {username},\n\n"
        f"{action_text}:\n"
        f"{link}\n\n"
        f"El enlace expira en {expiry_text}."
    )


def send_verification_email(user):
    link = _build_action_link(
        user.id, "email_verification", 1440, "auth.verify_email"
    )
    body = _build_body(
        user.username,
        "Verifica tu cuenta haciendo click aqui",
        link,
        "24 horas"
    )
    _send_email(user.email, "Verifica tu cuenta - Verneris", body)


def send_password_reset_email(user):
    link = _build_action_link(
        user.id, "password_reset", 30, "auth.reset_password"
    )
    body = _build_body(
        user.username,
        "Cambia tu contraseña aqui",
        link,
        "30 minutos"
    )
    _send_email(user.email, "Recuperar contraseña - Verneris", body)
