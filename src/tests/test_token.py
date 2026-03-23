from src.services.auth_service import (
    generate_jwt, decode_jwt,
)


def test_generate_and_decode_jwt(app):
    with app.app_context():
        token = generate_jwt(1, purpose="general")
        payload = decode_jwt(token)
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["purpose"] == "general"


def test_decode_jwt_correct_purpose(app):
    with app.app_context():
        token = generate_jwt(
            1, purpose="email_verification"
        )
        payload = decode_jwt(
            token, expected_purpose="email_verification"
        )
        assert payload is not None
        assert payload["user_id"] == 1


def test_decode_jwt_wrong_purpose_returns_none(app):
    with app.app_context():
        token = generate_jwt(
            1, purpose="email_verification"
        )
        payload = decode_jwt(
            token, expected_purpose="password_reset"
        )
        assert payload is None


def test_decode_jwt_expired_returns_none(app):
    with app.app_context():
        token = generate_jwt(
            1, purpose="general", expires_minutes=-1
        )
        payload = decode_jwt(token)
        assert payload is None


def test_decode_jwt_invalid_token_returns_none(app):
    with app.app_context():
        payload = decode_jwt("invalid.token.here")
        assert payload is None
