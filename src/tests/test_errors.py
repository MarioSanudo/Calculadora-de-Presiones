from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError


# --- Handlers de error HTTP ---

def test_404_devuelve_pagina_correcta(client):
    resp = client.get("/ruta-que-no-existe")
    assert resp.status_code == 404
    assert b"404" in resp.data


def test_404_contiene_enlace_a_home(client):
    resp = client.get("/ruta-que-no-existe")
    assert b"Volver al inicio" in resp.data


def test_ruta_anidada_inexistente_devuelve_404(client):
    resp = client.get("/auth/esto-no-existe")
    assert resp.status_code == 404


# --- Rate limit (429) en registro ---

def test_register_rate_limit_devuelve_429(client):
    data = {
        "username": "Carlos",
        "surname": "García",
        "email": "rl{}@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }
    # El límite es 10 por minuto; petición 11 debe devolver 429
    for i in range(10):
        d = dict(data)
        d["email"] = f"rl{i}@example.com"
        client.post("/auth/register", data=d)

    d = dict(data)
    d["email"] = "rl_extra@example.com"
    resp = client.post("/auth/register", data=d)
    assert resp.status_code == 429


def test_429_contiene_mensaje_espera(client):
    data = {
        "username": "Test",
        "surname": "User",
        "email": "t@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123"
    }
    for i in range(10):
        d = dict(data)
        d["email"] = f"t{i}@example.com"
        client.post("/auth/register", data=d)

    resp = client.post("/auth/register", data=data)
    assert b"Demasiadas peticiones" in resp.data


# --- Rate limit (429) en login ---

def test_login_rate_limit_devuelve_429(client):
    # El límite es 10 por minuto; petición 11 debe devolver 429
    payload = {"email": "x@example.com", "password": "cualquiera"}
    for _ in range(10):
        client.post("/auth/login", data=payload)

    resp = client.post("/auth/login", data=payload)
    assert resp.status_code == 429


# --- Error de BD en registro (500 → flash) ---

def test_register_db_error_muestra_mensaje(client):
    with patch(
        "src.routes.auth.create_user",
        side_effect=SQLAlchemyError("fallo simulado")
    ):
        resp = client.post("/auth/register", data={
            "username": "Ana",
            "surname": "Ruiz",
            "email": "ana@example.com",
            "password": "Securepass1!",
            "confirm_password": "Securepass1!"
        })
    assert resp.status_code == 200
    assert b"Error al crear la cuenta" in resp.data


def test_register_db_error_no_redirige(client):
    """Si falla el commit, permanecemos en el form."""
    with patch(
        "src.routes.auth.create_user",
        side_effect=SQLAlchemyError("fallo simulado")
    ):
        resp = client.post("/auth/register", data={
            "username": "Bob",
            "surname": "Smith",
            "email": "bob@example.com",
            "password": "Securepass1!",
            "confirm_password": "Securepass1!"
        })
    assert resp.status_code == 200
    assert b"Registrarse" in resp.data
