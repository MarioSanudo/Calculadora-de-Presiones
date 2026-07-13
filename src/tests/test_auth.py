from unittest.mock import patch, Mock
from sqlalchemy.exc import SQLAlchemyError
from src.models.user import User
from src.services.auth_service import generate_jwt
import pytest, jwt
from urllib.parse import urlsplit, parse_qs
from flask import redirect, url_for

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
        }, follow_redirects=True)   #Para que busque en todas las peticiones hasta llegar a la que no es una redirección (302)
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            email="test@example.com"
        ).first()
        assert user is not None
        assert user.username == "Carlos"
        assert user.is_verified is False


def test_register_email_stored_lowercase(client, app):
    """El email se persiste en minúsculas independientemente del input."""
    with patch("src.routes.auth.send_verification_email"):
        client.post("/auth/register", data={
            "username": "LowerTest",
            "surname": "Mail",
            "email": "UPPER@Example.COM",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        })

    with app.app_context():
        user = User.query.filter_by(
            email="upper@example.com"
        ).first()
        assert user is not None
        assert user.email == "upper@example.com"


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
    """Nombre+apellido duplicado → se añade sufijo numérico al username."""
    data = {
        "username": "Pedro",
        "surname": "Sanchez",
        "email": "pedro1@example.com",
        "password": _VALID_PASS,
        "confirm_password": _VALID_PASS,
    }
    with patch("src.routes.auth.send_verification_email"):  #Solo hago patch, quiero anular el envió de email, pero no necesito de ello sustituirlo por otro valor para que funcione el endpoint y su respuesta
        client.post("/auth/register", data=data)

    with patch("src.routes.auth.send_verification_email"):
        resp = client.post("/auth/register", data={
            "username": "Pedro",
            "surname": "Sanchez",
            "email": "pedro2@example.com",
            "password": _VALID_PASS,
            "confirm_password": _VALID_PASS,
        }, follow_redirects=True)

    assert resp.status_code == 200
    with app.app_context():
        user = User.query.filter_by(
            email="pedro2@example.com"
        ).first()
        assert user is not None
        assert user.username == "Pedro2"


def test_register_name_rejects_numbers(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos123",            #No hace falta patch, porque no se llega a la parte del servicio email externo, al no cumplir condiciones
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
    assert "Debe contener al menos una" in html #No hace falta por temas de recursos poner el (b), dado que se ha decodificado de bits a formato utf-8 que es el html


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
        "password": verified_user["password"],  #Esta función, pertenece a un usuario correcto que ya se creo en conftest.py
    })
    assert resp.status_code == 302  #Al no poner follow_redirects=True, lo manejamos de esta forma, pero la comprobación es igual de fiable
    assert resp.location == "/" or resp.location=="/calcular"


def test_login_wrong_password(client, verified_user):
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": "badpassword99!A",
    }, follow_redirects=True)
    assert b"incorrectos" in resp.data
    assert resp.location == None
    assert resp.status_code == 200 and resp.request.path == "/auth/login"


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
    assert b"Email no verificado" in resp.data


# ── Next param ──────────────────────────────────────

def _login_verified(client, verified_user, next_url=None):  #Con guión bajo, porque va a ser utilizada por otras funciones
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
        client, verified_user, "https://evil.com"   #Lo rechaza devuelve next_url=None y coge la redirección de serie que es hacia el endpoint de calculo
    )
    assert resp.status_code == 302
    assert resp.location == "/calcular"


def test_login_next_javascript(client, verified_user):
    resp = _login_verified(
        client, verified_user, "javascript:alert(1)"
    )
    assert resp.status_code == 302
    assert resp.location == "/calcular"


def test_login_next_protocol_relative(
    client, verified_user
):
    resp = _login_verified(
        client, verified_user, "//evil.com"
    )
    assert resp.status_code == 302
    assert resp.location == "/calcular"


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
    assert "Sesión cerrada" in resp.data.decode("utf-8")


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
        "src.services.email_service.mail.send"  #La acción de envio del email usando SMTP
    ) as mock_send:
        resp = client.post(
            "/auth/resend-verification",
            data={"email": "resend@example.com"},
            follow_redirects=True,
        )
        assert mock_send.called

    assert "Email de verificación enviado" in resp.data.decode("utf-8")


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
    assert "Recuperar contraseña" in resp.data.decode("utf-8")


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
    assert "Contraseña cambiada" in resp.data.decode("utf-8")

    # Verificar que el login funciona con la nueva pass
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": new_pass,
    })
    assert resp.status_code == 302
    assert resp.location == "/calcular"


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
    assert "inválido o expirado" in resp.data.decode("utf-8")


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

    assert "Error al cambiar la contraseña" in resp.data.decode("utf-8")

    # La contrasena original sigue funcionando
    resp = client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })
    assert resp.status_code == 302
    assert resp.location == "/calcular"


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
    assert "inválido o expirado" in resp.data.decode("utf-8")


# ── Token recycling ─────────────────────────────────

def test_verify_email_token_recycling_blocked(
    client, app, verified_user
):
    """Usuario A logueado no puede usar token de verificación de B."""
    # Crear usuario B sin verificar
    with app.app_context():
        from src.utils.extensions import db
        user_b = User(
            username="Victim",
            surname="User",
            email="victim@example.com",
            password_hash="hashed",
            is_verified=False,
        )
        db.session.add(user_b)
        db.session.commit()
        token_b = generate_jwt(
            user_b.id, purpose="email_verification"
        )

    # Login como usuario A
    client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })

    resp = client.get(
        f"/auth/verify/{token_b}",
        follow_redirects=True,
    )
    assert "Accion no permitida estas intentando atacar" in resp.data.decode("utf-8")

    # B sigue sin verificar
    with app.app_context():
        user_b = User.query.filter_by(
            email="victim@example.com"
        ).first()
        assert user_b.is_verified is False


def test_reset_password_token_recycling_blocked(
    client, app, verified_user
):
    """Usuario A logueado no puede usar token de reset de B."""
    with app.app_context():
        from src.utils.extensions import db
        from src.services.auth_service import hash_password
        user_b = User(
            username="Victim2",
            surname="User",
            email="victim2@example.com",
            password_hash=hash_password("Original1!"),
            is_verified=True,
        )
        db.session.add(user_b)
        db.session.commit()
        token_b = generate_jwt(
            user_b.id, purpose="password_reset"
        )

    # Login como usuario A
    client.post("/auth/login", data={
        "email": verified_user["email"],
        "password": verified_user["password"],
    })

    resp = client.post(
        f"/auth/reset-password/{token_b}",
        data={
            "password": "Hacked123!",
            "confirm_password": "Hacked123!",
        },
        follow_redirects=True,
    )
    assert "Acci" in resp.data.decode("utf-8")
    assert "no permitida" in resp.data.decode("utf-8")

    # La contraseña de B no cambió
    from src.services.auth_service import check_password
    with app.app_context():
        user_b = User.query.filter_by(
            email="victim2@example.com"
        ).first()
        assert check_password(user_b.password_hash, "Original1!")


# ── Google OAuth ────────────────────────────────────

def test_google_login_redirects(app, client):
    with patch("authlib.integrations.flask_client.apps.FlaskOAuth2App.load_server_metadata") as mock_google_metadata:
        mock_google_metadata.return_value={
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",   #El authorization_endpoint es lo mínimo necesario para que pueda hacerse la redirección
            "token_endpoint": "https://oauth2.googleapis.com/token"}
        
        resp = client.get("/auth/login/google")

        
    assert resp.status_code == 302
    assert "accounts.google.com" in resp.location
    print(urlsplit(resp.location).query)

    redirect_uri = parse_qs(urlsplit(resp.location).query)["redirect_uri"][0]
    #query=str(urlsplit(resp.location).query).split("&")[2].split("=")[1] Esta versión de aquí es demasiado hardcodeada, a la que se añadan campos se rompe el test
    with app.test_request_context():
        expected_callback = url_for('auth.google_callback', _external=True) #_external me aporta el scheme de la url necesario para que coincida

    assert redirect_uri == expected_callback


def test_google_login_redirects_mock_object(app, client):   #Ahora mockeo antes y tengo que devolver un tipo de info diferente el objeto de respuesta, no el contenido que se hace redirección
    with patch("src.routes.auth.oauth.google.authorize_redirect") as mock_authorize:
        mock_authorize.return_value = redirect("https://accounts.google.com/o/oauth2/v2/auth")  #Si devuelvo el json esa va a ser la respuesta, no se hace redirect por debajo porque estoy mockeando una acción anterior
        resp = client.get("/auth/login/google") #Daria un 200 != 302 porque tengo que ser explicito con el redirect en este mock

    assert resp.status_code == 302  #Es equivalente al anterior
    assert "accounts.google.com" in resp.location


def test_google_callback_new_user(client, app):
    mock_token = {      #Preconfigurado por eso lo hago de esta manera y lo paso al patch
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
        assert user.password_hash.startswith("$2b$")


def test_google_callback_existing_email_links(
    client, app, verified_user):
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


def test_decode_token_alg_None(app, client, caplog):
    with app.app_context():
        token_alg_none="eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjo0LCJwdXJwb3NlIjpudWxsLCJleHBpcmVfbWludXRlcyI6NjB9." # contenido = {"user_id": 4, "purpose": None, "expire_minutes": 60}   con alg:None habiendolo generado
        resp = client.get(f"/auth/verify/{token_alg_none}", follow_redirects=True) 
        
        assert b"Enlace invalido o expirado" in resp.data
        assert "Estan intentando modificar el token" in caplog.text #Capturo que se cumpla el contenido del log en petición y que la func individual devuelva lo que debe


#Revisar las nuevas funciones si un usuario se salta checkeo de WTF form
def test_check_login_data_no_wtf_bad_password_length(app, client, verified_user):
    resp= client.post("auth/login", data={
        "email": verified_user["email"],
        "password":"A1!" + "a"*200 #Contraseña larga, no hay comprobación de wtf
    })
    assert b"No cumple la longitud adecuada" in resp.data and b"8 caracter" in resp.data
    assert resp.status_code == 200

def test_check_login_no_wtf_bad_password_format(app, client, verified_user, caplog):
    resp= client.post("auth/login", data={
        "email": verified_user["email"],
        "password":"mario_admin12!"
    })
    assert "Debe contener al menos una mayúscula" in resp.data.decode("utf-8")
    assert "(no puedo mostrar la password), si cumple email es la otra causa" in caplog.text
    assert resp.status_code == 200 

def test_check_login_no_wtf_bad_password_key(app, client, verified_user, caplog):
    with patch("src.routes.forms.auth_forms.LoginForm.validate_on_submit", lambda self: True):
        resp= client.post("auth/login", data ={
            "email":verified_user["email"],
            "contra":verified_user["password"]  #La clave es password, contra no existe imagino que ese campo reciba un None
        })

    assert "No cumple la longitud adecuada de contraseña mínimo 8 caracter y máximo de 128, porfavor ajustese" in resp.data.decode("utf-8")
    assert resp.status_code == 200

def test_login_wtf_no_pass(app, client, verified_user):
    resp= client.post("auth/login", data={
        "email":verified_user["email"],
        "contra": verified_user["password"]
    })

    assert "This field is required." in resp.data.decode("utf-8")   #En cambio en este test se activa la protección de WTF
    assert resp.status_code == 200

def test_check_login_no_wtf_bad_email_key(app, client, verified_user):
    with patch("src.routes.forms.auth_forms.LoginForm.validate_on_submit",
               autospec=True, return_value= True):  #El spec para que detecte el mock necesario en el id del validate_on_submit, la otra forma más entendible a lambda self:True

        resp=client.post("auth/login", data={
            "email":None,
            "password": verified_user["password"]
        })
    
    assert "El formato del email no es correcto" in resp.data.decode("utf-8")
    assert resp.status_code == 200


def test_check_login_no_wtf_no_email_key(app, client, verified_user):
    with patch("src.routes.forms.auth_forms.LoginForm.validate_on_submit",
               autospec=True, return_value= True):

        resp=client.post("auth/login", data={
            "password": verified_user["password"]
        })
    
    assert "El formato del email no es correcto" in resp.data.decode("utf-8")
    assert resp.status_code == 200