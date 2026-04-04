from src.models.analysis import Analysis
from src.utils.extensions import db as _db


_VALID_PASS = "Securepass1!"

# Datos de cálculo válidos para reutilizar en los tests
_CALC_DATA = {
    "rider_weight": "70",
    "bike_weight": "8",
    "tire_width": "28",
    "inner_rim_width": "23",
    "wheel_diameter": "622",
    "tire_casing": "TIRE_CASING_STANDARD",
    "ride_style": "RIDE_STYLE_ROAD",
    "rim_type": "RIM_TYPE_TUBES",
    "surface": "SURFACE_DRY",
}


def _login(client, email, password):
    """Helper para loguear un usuario en el test client."""
    return client.post("/auth/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)


# ── Acceso sin login ────────────────────────────────

def test_calcular_requiere_login(client):
    """GET /calcular sin login redirige a login."""
    resp = client.get("/calcular")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_historial_requiere_login(client):
    """GET /historial sin login redirige a login."""
    resp = client.get("/historial")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_guardar_requiere_login(client):
    """POST /analisis/guardar sin login redirige."""
    resp = client.post("/analisis/guardar", data=_CALC_DATA)
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


# ── Calcular con login ──────────────────────────────

def test_calcular_con_login(client, verified_user):
    """GET /calcular con usuario logueado devuelve 200."""
    _login(client, verified_user["email"], verified_user["password"])
    resp = client.get("/calcular")
    assert resp.status_code == 200
    assert b"Calculadora" in resp.data


def test_calcular_post_muestra_resultado(client, verified_user):
    """POST /calcular devuelve presiones front/rear."""
    _login(client, verified_user["email"], verified_user["password"])
    resp = client.post("/calcular", data=_CALC_DATA)
    assert resp.status_code == 200
    assert b"bar" in resp.data
    assert b"psi" in resp.data


# ── Guardar análisis ────────────────────────────────

def test_guardar_analisis_ok(client, verified_user, app):
    """POST /analisis/guardar crea fila en analyses."""
    _login(client, verified_user["email"], verified_user["password"])
    resp = client.post("/analisis/guardar", data=_CALC_DATA)
    assert resp.status_code == 200
    assert "guardado" in resp.data.decode().lower()

    with app.app_context():
        count = Analysis.query.count()
        assert count == 1
        a = Analysis.query.first()
        assert a.rider_weight == 70.0
        assert a.front_bar > 0
        assert a.rear_bar > 0


def test_guardar_datos_invalidos(client, verified_user, app):
    """POST /analisis/guardar con datos malos no crea fila."""
    _login(client, verified_user["email"], verified_user["password"])
    bad_data = _CALC_DATA.copy()
    bad_data["rider_weight"] = "999"  # fuera de rango
    resp = client.post("/analisis/guardar", data=bad_data)
    assert resp.status_code == 200
    assert "no válidos" in resp.data.decode().lower()

    with app.app_context():
        assert Analysis.query.count() == 0


# ── Historial ───────────────────────────────────────

def test_historial_muestra_analisis(
    client, verified_user, app
):
    """GET /historial muestra los análisis guardados."""
    _login(client, verified_user["email"], verified_user["password"])
    # Guardar un análisis primero
    client.post("/analisis/guardar", data=_CALC_DATA)

    resp = client.get("/historial")
    assert resp.status_code == 200
    assert b"Carretera" in resp.data
    assert b"bar" in resp.data


def test_historial_vacio(client, verified_user):
    """GET /historial sin análisis muestra mensaje vacío."""
    _login(client, verified_user["email"], verified_user["password"])
    resp = client.get("/historial")
    assert resp.status_code == 200
    assert "no tienes" in resp.data.decode().lower()


def test_historial_no_muestra_de_otro_usuario(
    client, app, verified_user
):
    """Un usuario no ve los análisis de otro."""
    from src.models.user import User
    from src.services.auth_service import hash_password

    _login(client, verified_user["email"], verified_user["password"])
    client.post("/analisis/guardar", data=_CALC_DATA)
    client.post("/auth/logout")

    # Crear segundo usuario
    with app.app_context():
        user2 = User(
            username="Otro",
            surname="Usuario",
            email="otro@example.com",
            password_hash=hash_password(_VALID_PASS),
            is_verified=True,
        )
        _db.session.add(user2)
        _db.session.commit()

    _login(client, "otro@example.com", _VALID_PASS)
    resp = client.get("/historial")
    assert resp.status_code == 200
    assert "no tienes" in resp.data.decode().lower()
