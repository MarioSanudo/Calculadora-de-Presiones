from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from src.services.pressure_service import (
    validate_inputs,
    calculate_pressure
)
from src.services.pressure_service import to_float, to_int
from src.models.analysis import Analysis
from src.utils.pressure_constants import RIDE_STYLE_DEFAULTS
from src.utils.extensions import db, limiter

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # En Fase 2 redirigirá a la calculadora si está autenticado
    return render_template("index.html")



@main_bp.route("/calcular", methods=["GET", "POST"])
@login_required
@limiter.limit("20 per minute")
def calcular_presion():
    all_defaults = RIDE_STYLE_DEFAULTS
    if request.method == "POST":
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
            errors=[],
            result=result,
            data=data)

    return render_template(
        "calculator/index.html",
        all_defaults=all_defaults)


@main_bp.route("/analisis/guardar", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def guardar_analisis():
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

    # Validar y recalcular server-side
    errors = validate_inputs(data)
    if errors:
        return render_template(
            "calculator/_save_feedback.html",
            success=False,
            message="Datos no válidos.")

    result = calculate_pressure(data)

    analysis = Analysis(
        user_id=current_user.id,
        rider_weight=data["rider_weight"],
        bike_weight=data["bike_weight"],
        tire_width=data["tire_width"],
        inner_rim_width=data["inner_rim_width"],
        wheel_diameter=data["wheel_diameter"],
        tire_casing=data["tire_casing"],
        ride_style=data["ride_style"],
        rim_type=data["rim_type"],
        surface=data["surface"],
        front_bar=result["front"]["bar"],
        front_psi=result["front"]["psi"],
        rear_bar=result["rear"]["bar"],
        rear_psi=result["rear"]["psi"]
    )

    try:
        db.session.add(analysis)
        db.session.commit()
        return render_template(
            "calculator/_save_feedback.html",
            success=True,
            message="Análisis guardado correctamente.")
    except Exception:
        db.session.rollback()
        return render_template(
            "calculator/_save_feedback.html",
            success=False,
            message="Error al guardar el análisis.")


@main_bp.route("/historial")
@login_required
def historial():
    analyses = (
        current_user.analyses
        .order_by(Analysis.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template(
        "history/index.html",
        analyses=analyses)