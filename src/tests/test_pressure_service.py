import pytest
from src.services.pressure_service import (
    calculate_pressure,
    validate_inputs,
    get_rim_ref)

# Caso base del skill de presiones:
# 60kg ciclista, 8kg bici, 28mm, aro 23mm interno, 700c,
# carretera, seco, cámara, carcasa estándar.
BASE_DATA = {
    "rider_weight":     60.0,
    "bike_weight":      8.0,
    "tire_width_front": 28.0,
    "tire_width_rear":  28.0,
    "inner_rim_width":  23.0,
    "wheel_diameter":   622,
    "tire_casing":      "TIRE_CASING_STANDARD",
    "ride_style":       "RIDE_STYLE_ROAD",
    "rim_type":         "RIM_TYPE_TUBES",
    "surface":          "SURFACE_DRY",
    "tire_brand":       "TIRE_BRAND_GENERAL",
    "altitude":         0,
    "temp_exterior":    20.0,
}


def test_caso_base():
    """Verifica el caso base del skill: ~57.2 PSI delantera, ~60.8 PSI trasera."""
    result = calculate_pressure(BASE_DATA)
    assert abs(result["front"]["psi"] - 57.2) < 0.5
    assert abs(result["rear"]["psi"] - 60.8) < 0.5


def test_valores_intermedios():
    """Verifica los pasos intermedios de la fórmula."""
    # 28mm → rango 25-29 en la tabla → aro de referencia 19mm
    assert get_rim_ref(28.0, "TIRE_BRAND_GENERAL") == 19
    # effective_width = 28 + 0.4 * (23 - 19) = 29.6
    assert 28.0 + 0.4 * (23.0 - 19.0) == pytest.approx(29.6)


def test_estructura_resultado():
    """El resultado tiene la estructura correcta con bar y psi."""
    result = calculate_pressure(BASE_DATA)
    assert "front" in result and "rear" in result
    for wheel in ("front", "rear"):
        assert "bar" in result[wheel]
        assert "psi" in result[wheel]
    # bar ≈ psi / 14.5038
    assert result["front"]["bar"] == pytest.approx(
        result["front"]["psi"] / 14.5038, abs=0.01
    )


def test_trasera_mayor_que_delantera():
    """La rueda trasera siempre lleva más presión que la delantera."""
    result = calculate_pressure(BASE_DATA)
    assert result["rear"]["psi"] > result["front"]["psi"]


class TestValidateInputs:

    def test_datos_validos(self):
        """Datos correctos → lista vacía."""
        assert validate_inputs(BASE_DATA) == []

    def test_campo_faltante(self):
        data = {k: v for k, v in BASE_DATA.items() if k != "rider_weight"}
        errors = validate_inputs(data)
        assert any("rider_weight" in e for e in errors)

    def test_rider_weight_muy_bajo(self):
        data = {**BASE_DATA, "rider_weight": 0}
        errors = validate_inputs(data)
        assert any("ciclista" in e for e in errors)

    def test_rider_weight_muy_alto(self):
        data = {**BASE_DATA, "rider_weight": 300}
        errors = validate_inputs(data)
        assert any("ciclista" in e for e in errors)

    def test_bike_weight_fuera_rango(self):
        data = {**BASE_DATA, "bike_weight": 30}
        errors = validate_inputs(data)
        assert any("bici" in e for e in errors)

    def test_ride_style_invalido(self):
        data = {**BASE_DATA, "ride_style": "RIDE_STYLE_MTB"}
        errors = validate_inputs(data)
        assert any("Modalidad" in e for e in errors)

    def test_tire_width_fuera_rango_road(self):
        """15mm está por debajo del mínimo para carretera (18mm)."""
        data = {**BASE_DATA, "tire_width_front": 15, "tire_width_rear": 15}
        errors = validate_inputs(data)
        assert any("Ancho" in e for e in errors)

    def test_tire_width_road_tubeless_crochet_max(self):
        """Road + tubeless crochet → máximo 50mm."""
        data = {
            **BASE_DATA,
            "rim_type":        "RIM_TYPE_TUBELESS_CROCHET",
            "tire_width_front": 60.0,
            "tire_width_rear":  60.0,
        }
        errors = validate_inputs(data)
        assert any("Ancho" in e for e in errors)

    def test_inner_rim_tubular_debe_ser_32(self):
        """Aro tubular tiene anchura interior fija de 32mm."""
        data = {
            **BASE_DATA,
            "rim_type":        "RIM_TYPE_TUBULAR",
            "inner_rim_width": 25.0,
        }
        errors = validate_inputs(data)
        assert any("tubular" in e.lower() for e in errors)

    def test_inner_rim_tubular_correcto(self):
        """Aro tubular con 32mm → sin error de anchura."""
        data = {
            **BASE_DATA,
            "rim_type":        "RIM_TYPE_TUBULAR",
            "inner_rim_width": 32.0,
        }
        errors = validate_inputs(data)
        assert not any("tubular" in e.lower() for e in errors)

    def test_wheel_diameter_invalido(self):
        """700 no es un diámetro válido (el correcto es 622 para 700c)."""
        data = {**BASE_DATA, "wheel_diameter": 700}
        errors = validate_inputs(data)
        assert any("700" in e for e in errors)

    def test_surface_invalida(self):
        data = {**BASE_DATA, "surface": "SURFACE_MUD"}
        errors = validate_inputs(data)
        assert any("Superficie" in e for e in errors)
