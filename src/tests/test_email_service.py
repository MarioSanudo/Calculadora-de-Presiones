from unittest.mock import patch, MagicMock
from src.services.email_service import (
    _build_body,
    _build_action_link,
    send_verification_email,
    send_password_reset_email,
)


# ── _build_body ──────────────────────────────────────

def test_build_body_contains_username():
    body = _build_body("Carlos", "Accion aqui", "http://link", "24 horas")
    assert "Hola Carlos" in body


def test_build_body_contains_action_text():
    body = _build_body("Carlos", "Verifica tu cuenta", "http://link", "24 horas")
    assert "Verifica tu cuenta" in body


def test_build_body_contains_link():
    body = _build_body("Carlos", "Accion", "http://example.com/t", "30 minutos")
    assert "http://example.com/t" in body


def test_build_body_contains_expiry():
    body = _build_body("Carlos", "Accion", "http://link", "30 minutos")
    assert "30 minutos" in body


# ── _build_action_link ───────────────────────────────

def test_build_action_link_calls_generate_jwt(app):
    with app.app_context():
        with patch(
            "src.services.email_service.generate_jwt",
            return_value="fake-token",
        ) as mock_jwt, patch(
            "src.services.email_service.url_for",
            return_value="http://localhost/auth/verify/fake-token",
        ) as mock_url:
            result = _build_action_link(
                42, "email_verification", 1440, "auth.verify_email"
            )
            mock_jwt.assert_called_once_with(
                42,
                purpose="email_verification",
                expires_minutes=1440,
            )
            mock_url.assert_called_once_with(
                "auth.verify_email",
                token="fake-token",
                _external=True,
            )
            assert result == "http://localhost/auth/verify/fake-token"


# ── send_verification_email ──────────────────────────

def test_send_verification_email_calls_send(app):
    user = MagicMock()
    user.id = 1
    user.username = "Carlos"
    user.email = "carlos@example.com"

    with app.app_context():
        with patch(
            "src.services.email_service._build_action_link",
            return_value="http://link",
        ), patch(
            "src.services.email_service._send_email"
        ) as mock_send:
            send_verification_email(user)
            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert args[0] == "carlos@example.com"
            assert "Verifica" in args[1]
            assert "Carlos" in args[2]


# ── send_password_reset_email ────────────────────────

def test_send_password_reset_email_calls_send(app):
    user = MagicMock()
    user.id = 2
    user.username = "Ana"
    user.email = "ana@example.com"

    with app.app_context():
        with patch(
            "src.services.email_service._build_action_link",
            return_value="http://link",
        ), patch(
            "src.services.email_service._send_email"
        ) as mock_send:
            send_password_reset_email(user)
            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert args[0] == "ana@example.com"
            assert "contrase" in args[1].lower()
            assert "Ana" in args[2]
