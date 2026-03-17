import pytest
from src.utils.validators import validar_next


# --- Casos válidos ---

def test_ruta_interna_simple():
    assert validar_next("/dashboard") == "/dashboard"


def test_ruta_interna_con_query():
    assert validar_next("/perfil?tab=historial") == "/perfil?tab=historial"


def test_ruta_interna_anidada():
    assert validar_next("/auth/login") == "/auth/login"


# --- Casos inválidos: valores vacíos o tipos erróneos ---

def test_none_devuelve_false():
    assert validar_next(None) is False


def test_string_vacio_devuelve_false():
    assert validar_next("") is False


def test_no_string_devuelve_false():
    assert validar_next(123) is False


def test_url_demasiado_larga():
    url_larga = "/" + "a" * 2049
    assert validar_next(url_larga) is False


# --- Open redirect: schemes externos ---

def test_scheme_http_bloqueado():
    assert validar_next("http://evil.com") is False


def test_scheme_https_bloqueado():
    assert validar_next("https://evil.com/robo") is False


def test_scheme_javascript_bloqueado():
    assert validar_next("javascript:alert(1)") is False


def test_scheme_data_bloqueado():
    assert validar_next("data:text/html,<script>alert(1)</script>") is False


def test_scheme_vbscript_bloqueado():
    assert validar_next("vbscript:msgbox(1)") is False


# --- Open redirect: rutas con dominio externo ---

def test_protocol_relative_bloqueado():
    """//evil.com se interpreta como dominio externo en navegadores."""
    assert validar_next("//evil.com") is False


def test_ruta_sin_barra_inicial_bloqueada():
    """Sin / al inicio no es una ruta interna válida."""
    assert validar_next("evil.com/ruta") is False


def test_ruta_relativa_sin_barra_bloqueada():
    assert validar_next("dashboard") is False
