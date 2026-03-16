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
        "username": "Carlos",
        "surname": "García",
        "email": "test@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }, follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        assert user.username == "Carlos"
        assert user.surname == "García"


def test_register_duplicate_email(client, app):
    data = {
        "username": "Ana",
        "surname": "López",
        "email": "dup@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }
    client.post("/auth/register", data=data)

    resp = client.post("/auth/register", data={
        "username": "Ana",
        "surname": "Martínez",
        "email": "dup@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })
    assert b"ya esta registrado" in resp.data


def test_register_duplicate_name(client, app):
    data = {
        "username": "Pedro",
        "surname": "Sánchez",
        "email": "pedro1@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }
    client.post("/auth/register", data=data)

    resp = client.post("/auth/register", data={
        "username": "Pedro",
        "surname": "Sánchez",
        "email": "pedro2@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })
    assert b"ya estan registrados" in resp.data


def test_register_name_rejects_numbers(client):
    resp = client.post("/auth/register", data={
        "username": "Carlos123",
        "surname": "García",
        "email": "num@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })
    # El form debe rechazarlo (no redirige, vuelve a mostrar el formulario)
    assert resp.status_code == 200
    assert b"num@example.com" not in resp.data or b"Solo letras" in resp.data


def test_login_success(client):
    client.post("/auth/register", data={
        "username": "Laura",
        "surname": "Fernández",
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
        "username": "Miguel",
        "surname": "Torres",
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
        "username": "Julia",
        "surname": "Romero",
        "email": "logout@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    })
    client.post("/auth/login", data={
        "email": "logout@example.com",
        "password": "securepass123"
    })

    resp = client.post("/auth/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Sesion cerrada" in resp.data
