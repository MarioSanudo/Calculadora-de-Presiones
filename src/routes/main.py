from flask import Blueprint, render_template, request
from flask_login import current_user
from src.services.pressure_service import (
    validate_inputs,
    calculate_pressure
)
from src.services.pressure_service import to_float, to_int
from src.utils.pressure_constants import RIDE_STYLE_DEFAULTS
from src.utils.extensions import limiter

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # En Fase 2 redirigirá a la calculadora si está autenticado
    return render_template("index.html")



@main_bp.route("/calcular", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def calcular_presion():
    defaults = RIDE_STYLE_DEFAULTS.get("RIDE_STYLE_ROAD")

    if request.method=="POST":
        data = {
            "rider_weight":    to_float(request.form.get("rider_weight")),
            "bike_weight":     to_float(request.form.get("bike_weight")),
            "tire_width":      to_float(request.form.get("tire_width")),
            "inner_rim_width": to_float(request.form.get("inner_rim_width")),
            "wheel_diameter":  to_int(request.form.get("wheel_diameter")),
            "tire_casing":     request.form.get("tire_casing"),
            "ride_style":      request.form.get("ride_style"),
            "rim_type":        request.form.get("rim_type"),
            "surface":         request.form.get("surface")
            }

        errors = validate_inputs(data)
        if errors:
            return render_template(
                "calculator/_result.html",
                errors=errors,
                result=None)

        result = calculate_pressure(data)
        return render_template(
            "calculator/_result.html",
            errors=[],  #Se muestra la lista vacía en el html, es decir nada
            result=result)

    return render_template("calculator/index.html", defaults=defaults)