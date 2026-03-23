from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from src.models.user import User
from src.services.auth_service import generate_jwt

# Contrasena valida: mayuscula + caracter especial + longitud
_VALID_PASS = "Securepass1!"


# ── Registro ────────────────────────────────────────

def test_register_page_loads(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200
    assert b"Crear cuenta" in resp.data


def test_login_page_loads(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Iniciar sesion" in resp.data


def test_register_success(client, app):
    with patch("src.routes.auth.send_verification_email"):
        resp = client.post("/auth/register", data={
            "username": "Carlos",
            "surname": "Garcia",
            "email": "test@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        }, follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            email="test@example.com"
        ).first()
        assert user is not None
        assert user.username == "Carlos"
        assert user.is_verified is False


def test_register_duplicate_email(client, app):
    data = {
        "username": "Ana",
        "surname": "Lopez",
        "email": "dup@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    }
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data=data)

    resp = client.post("/auth/register", data={
        "username": "Ana",
        "surname": "Martinez",
        "email": "dup@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    })
    assert b"ya esta registrado" in resp.data


def test_register_duplicate_name(client, app):
    data = {
        "username": "Pedro",
        "surname": "Sanchez",
        "email": "pedro1@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    }
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data=data)

    resp = client.post("/auth/register", data={
        "username": "Pedro",
        "surname": "Sanchez",
        "email": "pedro2@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    })
    assert b"ya estan registrados" in resp.data


def test_register_name_rejects_numbers(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos123",
        "surname": "Garcia",
        "email": "num@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    })
    assert resp.status_code == 200
    assert b"Solo letras" in resp.data


def test_register_name_rejects_spaces(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos Luis",
        "surname": "Garcia",
        "email": "spaces@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    })
    assert resp.status_code == 200
    assert b"Solo letras" in resp.data


def test_register_name_rejects_hyphens(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos-Luis",
        "surname": "Garcia",
        "email": "hyphens@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    })
    assert resp.status_code == 200
    assert b"Solo letras" in resp.data


def test_register_password_rejects_no_uppercase(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos",
        "surname": "Garcia",
        "email": "noUpper@example.com",
        "password": "securepass1!",
        "confirm_password": "securepass1!",
    })
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Debe contener al menos una" in html


def test_register_password_rejects_no_special(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos",
        "surname": "Garcia",
        "email": "noSpecial@example.com",
        "password": "Securepass123",
        "confirm_password": "Securepass123",
    })
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Debe contener al menos una" in html


def test_register_password_rejects_both(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos",
        "surname": "Garcia",
        "email": "noBoth@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123",
    })
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Debe contener al menos una" in html


# ── Login (requiere verified_user) ──────────────────

def test_login_success(client, verified_user):
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })
    assert resp.status_code == 302
    assert resp.location == "/"


def test_login_wrong_password(client, verified_user):
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": "badpassword99!A",
    })
    assert b"incorrectos" in resp.data


def test_login_unverified_blocked(client, app):
    """Un usuario no verificado no puede hacer login."""
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "Unverified",
            "surname": "Test",
            "email": "unverified@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    resp = client.post("/auth/login", data={
        "email": "unverified@example.com",
        "password": _VALID_PASS,
    })
    assert b"Verifica tu email" in resp.data


# ── Next param ──────────────────────────────────────

def _login_verified(client, verified_user, next_url=None):
    url = (
        f"/auth/login?next={next_url}"
        if next_url else "/auth/login"
    )
    return client.post(url, data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })


def test_login_next_valido(client, verified_user):
    resp = _login_verified(
        client, verified_user, "/historial"
    )
    assert resp.status_code == 302
    assert resp.location == "/historial"


def test_login_next_externo(client, verified_user):
    resp = _login_verified(
        client, verified_user, "https://evil.com"
    )
    assert resp.status_code == 302
    assert resp.location == "/"


def test_login_next_javascript(client, verified_user):
    resp = _login_verified(
        client, verified_user, "javascript:alert(1)"
    )
    assert resp.status_code == 302
    assert resp.location == "/"


def test_login_next_protocol_relative(
    client, verified_user
):
    resp = _login_verified(
        client, verified_user, "//evil.com"
    )
    assert resp.status_code == 302
    assert resp.location == "/"


# ── Logout ──────────────────────────────────────────

def test_logout(client, verified_user):
    client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })
    resp = client.post(
        "/auth/logout", follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Sesion cerrada" in resp.data


# ── Email verification ──────────────────────────────

def test_verify_email_success(client, app):
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "Verify",
            "surname": "Test",
            "email": "verify@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    with app.app_context():
        user = User.query.filter_by(
            email="verify@example.com"
        ).first()
        token = generate_jwt(
            user.id, purpose="email_verification"
        )

    resp = client.get(
        f"/auth/verify/{token}",
        follow_redirects=True,
    )
    assert b"Email verificado" in resp.data

    with app.app_context():
        user = User.query.filter_by(
            email="verify@example.com"
        ).first()
        assert user.is_verified is True


def test_verify_email_expired_token(client, app):
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "Expired",
            "surname": "Token",
            "email": "expired@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    with app.app_context():
        user = User.query.filter_by(
            email="expired@example.com"
        ).first()
        token = generate_jwt(
            user.id,
            purpose="email_verification",
            expires_minutes=-1,
        )

    resp = client.get(
        f"/auth/verify/{token}",
        follow_redirects=True,
    )
    assert b"invalido o expirado" in resp.data


def test_verify_email_wrong_purpose(client, app):
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "Wrong",
            "surname": "Purpose",
            "email": "wrongp@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    with app.app_context():
        user = User.query.filter_by(
            email="wrongp@example.com"
        ).first()
        token = generate_jwt(
            user.id, purpose="password_reset"
        )

    resp = client.get(
        f"/auth/verify/{token}",
        follow_redirects=True,
    )
    assert b"invalido o expirado" in resp.data


def test_verify_email_db_error(client, app):
    """Fallo en commit → rollback, flash de error, user sigue sin verificar."""
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "DberrorV",
            "surname": "Test",
            "email": "dberrorv@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    with app.app_context():
        user = User.query.filter_by(
            email="dberrorv@example.com"
        ).first()
        token = generate_jwt(
            user.id, purpose="email_verification"
        )

    with patch(
        "src.routes.auth.db.session.commit",
        side_effect=SQLAlchemyError("db fail"),
    ):
        resp = client.get(
            f"/auth/verify/{token}",
            follow_redirects=True,
        )

    assert b"Error al verificar el email" in resp.data

    with app.app_context():
        user = User.query.filter_by(
            email="dberrorv@example.com"
        ).first()
        assert user.is_verified is False


def test_resend_verification_existing(client, app):
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "Resend",
            "surname": "Test",
            "email": "resend@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    with patch(
        "src.services.email_service.mail.send"
    ) as mock_send:
        resp = client.post(
            "/auth/resend-verification",
            data={"email": "resend@example.com"},
            follow_redirects=True,
        )
        assert mock_send.called

    assert b"Si el email existe" in resp.data


def test_resend_verification_nonexistent(client):
    resp = client.post(
        "/auth/resend-verification",
        data={"email": "noexiste@example.com"},
        follow_redirects=True,
    )
    assert b"Si el email existe" in resp.data


# ── Password reset ──────────────────────────────────

def test_forgot_password_page_loads(client):
    resp = client.get("/auth/forgot-password")
    assert resp.status_code == 200
    assert b"Recuperar contrasena" in resp.data


def test_forgot_password_sends_email(
    client, verified_user
):
    with patch(
        "src.services.email_service.mail.send"
    ) as mock_send:
        resp = client.post(
            "/auth/forgot-password",
            data={"email": verified_user["email"]},
            follow_redirects=True,
        )
        assert mock_send.called

    assert b"Si el email existe" in resp.data


def test_forgot_password_nonexistent(client):
    resp = client.post(
        "/auth/forgot-password",
        data={"email": "noexiste@example.com"},
        follow_redirects=True,
    )
    assert b"Si el email existe" in resp.data


def test_reset_password_success(
    client, app, verified_user
):
    with app.app_context():
        user = User.query.filter_by(
            email=verified_user["email"]
        ).first()
        token = generate_jwt(
            user.id, purpose="password_reset"
        )

    new_pass = "Newpass123!"
    resp = client.post(
        f"/auth/reset-password/{token}",
        data={
            "password": new_pass,
            "confirm_password": new_pass,
        },
        follow_redirects=True,
    )
    assert b"Contrasena cambiada" in resp.data

    # Verificar que el login funciona con la nueva pass
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": new_pass,
    })
    assert resp.status_code == 302
    assert resp.location == "/"


def test_reset_password_expired_token(
    client, app, verified_user
):
    with app.app_context():
        user = User.query.filter_by(
            email=verified_user["email"]
        ).first()
        token = generate_jwt(
            user.id,
            purpose="password_reset",
            expires_minutes=-1,
        )

    resp = client.get(
        f"/auth/reset-password/{token}",
        follow_redirects=True,
    )
    assert b"invalido o expirado" in resp.data


def test_reset_password_db_error(
    client, app, verified_user
):
    """Fallo en commit → rollback, flash de error, contrasena no cambia."""
    with app.app_context():
        user = User.query.filter_by(
            email=verified_user["email"]
        ).first()
        token = generate_jwt(
            user.id, purpose="password_reset"
        )

    new_pass = "Newpass123!"
    with patch(
        "src.routes.auth.db.session.commit",
        side_effect=SQLAlchemyError("db fail"),
    ):
        resp = client.post(
            f"/auth/reset-password/{token}",
            data={
                "password": new_pass,
                "confirm_password": new_pass,
            },
            follow_redirects=True,
        )

    assert b"Error al cambiar la contrasena" in resp.data

    # La contrasena original sigue funcionando
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })
    assert resp.status_code == 302
    assert resp.location == "/"


def test_reset_password_wrong_purpose(
    client, app, verified_user
):
    with app.app_context():
        user = User.query.filter_by(
            email=verified_user["email"]
        ).first()
        token = generate_jwt(
            user.id, purpose="email_verification"
        )

    resp = client.get(
        f"/auth/reset-password/{token}",
        follow_redirects=True,
    )
    assert b"invalido o expirado" in resp.data


# ── Google OAuth ────────────────────────────────────

def test_google_login_redirects(client):
    resp = client.get("/auth/login/google")
    assert resp.status_code == 302


def test_google_callback_new_user(client, app):
    mock_token = {
        "userinfo": {
            "sub": "google-id-123",
            "email": "googleuser@gmail.com",
            "given_name": "Google",
            "family_name": "User",
        }
    }
    with patch.object(
        app.extensions.get("authlib.integrations.flask_client", {}).get("google", type("", (), {"authorize_access_token": None})),
        "authorize_access_token",
        return_value=mock_token,
    ) if False else patch(
        "src.routes.auth.oauth.google"
        ".authorize_access_token",
        return_value=mock_token,
    ):
        resp = client.get(
            "/auth/login/google/callback",
            follow_redirects=True,
        )

    with app.app_context():
        user = User.query.filter_by(
            email="googleuser@gmail.com"
        ).first()
        assert user is not None
        assert user.is_verified is True
        assert user.google_id == "google-id-123"
        assert user.password_hash is None


def test_google_callback_existing_email_links(
    client, app, verified_user
):
    mock_token = {
        "userinfo": {
            "sub": "google-id-456",
            "email": verified_user["email"],
            "given_name": "Verified",
            "family_name": "User",
        }
    }
    with patch(
        "src.routes.auth.oauth.google"
        ".authorize_access_token",
        return_value=mock_token,
    ):
        resp = client.get(
            "/auth/login/google/callback",
            follow_redirects=True,
        )

    with app.app_context():
        user = User.query.filter_by(
            email=verified_user["email"]
        ).first()
        assert user.google_id == "google-id-456"


def test_google_callback_already_linked(
    client, app, verified_user
):
    with app.app_context():
        user = User.query.filter_by(
            email=verified_user["email"]
        ).first()
        user.google_id = "google-id-789"
        from src.utils.extensions import db
        db.session.commit()

    mock_token = {
        "userinfo": {
            "sub": "google-id-789",
            "email": verified_user["email"],
            "given_name": "Verified",
            "family_name": "User",
        }
    }
    with patch(
        "src.routes.auth.oauth.google"
        ".authorize_access_token",
        return_value=mock_token,
    ):
        resp = client.get(
            "/auth/login/google/callback",
            follow_redirects=True,
        )
    assert resp.status_code == 200
