from src.models.user import User


def test_register_page_loads(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200
    assert b"Crear cuenta" in resp.data


def test_login_page_loads(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Iniciar sesion" in resp.data


def test_register_success(client, app):
    resp = client.post("/auth/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }, follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            email="test@example.com"
        ).first()
        assert user is not None
        assert user.username == "testuser"


def test_register_duplicate_email(client, app):
    data = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }
    client.post("/auth/register", data=data)

    resp = client.post("/auth/register", data={
        "username": "user2",
        "email": "dup@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })
    assert b"ya esta registrado" in resp.data


def test_login_success(client):
    client.post("/auth/register", data={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })

    resp = client.post("/auth/login", data={
        "email": "login@example.com",
        "password": "securepass123"
    })
    assert resp.status_code == 302
    assert resp.location == "/"


def test_login_wrong_password(client):
    client.post("/auth/register", data={
        "username": "wrongpw",
        "email": "wrong@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })

    resp = client.post("/auth/login", data={
        "email": "wrong@example.com",
        "password": "badpassword99"
    })
    assert b"incorrectos" in resp.data


def test_logout(client):
    client.post("/auth/register", data={
        "username": "logoutuser",
        "email": "logout@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })
    client.post("/auth/login", data={
        "email": "logout@example.com",
        "password": "securepass123"
    })

    resp = client.post(
        "/auth/logout", follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Sesion cerrada" in resp.data
