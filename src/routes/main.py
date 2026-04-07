from flask import (
    Blueprint, render_template, request,
    current_app, flash, make_response, url_for
)
from flask_login import login_required, current_user
from src.services.pressure_service import (
    validate_inputs,
    calculate_pressure,
    check_pressure_warnings,
    to_float, to_int
)
from src.models.analysis import Analysis
from src.utils.pressure_constants import RIDE_STYLE_DEFAULTS
from src.utils.extensions import db, limiter
from sqlalchemy.exc import SQLAlchemyError

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
            "rider_weight":     to_float(request.form.get("rider_weight")),
            "bike_weight":      to_float(request.form.get("bike_weight")),
            "tire_width_front": to_float(request.form.get("tire_width_front")),
            "tire_width_rear":  to_float(request.form.get("tire_width_rear")),
            "inner_rim_width":  to_float(request.form.get("inner_rim_width")),
            "wheel_diameter":  to_int(request.form.get("wheel_diameter")),
            "tire_casing":     request.form.get("tire_casing"),
            "ride_style":      request.form.get("ride_style"),
            "rim_type":        request.form.get("rim_type"),
            "surface":         request.form.get("surface"),
            "tire_brand":      request.form.get("tire_brand"),
            "altitude":        to_float(request.form.get("altitude")),
            "temp_exterior":   to_float(request.form.get("temp_exterior"))
            }

        errors = validate_inputs(data)
        if errors:
            return render_template(
                "calculator/_result.html",
                errors=errors,
                result=None)

        try:
            result = calculate_pressure(data)
        except ValueError as e:
            return render_template(
                "calculator/_result.html",
                errors=[str(e)],
                result=None)
        check_pressure_warnings(result, data["rim_type"], data["ride_style"])

        if request.form.get("save") == "1":
            analysis = Analysis(
                user_id=current_user.id,
                rider_weight=data["rider_weight"],
                bike_weight=data["bike_weight"],
                tire_width_front=data["tire_width_front"],
                tire_width_rear=data["tire_width_rear"],
                inner_rim_width=data["inner_rim_width"],
                wheel_diameter=data["wheel_diameter"],
                tire_casing=data["tire_casing"],
                ride_style=data["ride_style"],
                rim_type=data["rim_type"],
                surface=data["surface"],
                altitude=data["altitude"],
                temp_exterior=data["temp_exterior"],
                front_bar=result["front"]["bar"],
                front_psi=result["front"]["psi"],
                rear_bar=result["rear"]["bar"],
                rear_psi=result["rear"]["psi"]
            )
            try:
                db.session.add(analysis)
                db.session.commit()
                saved = True
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(
                    "Error guardando análisis user_id=%s: %s",
                    current_user.id, e, exc_info=True
                )
                saved = False
        else:
            saved = None

        return render_template(
            "calculator/_result.html",
            errors=[],
            result=result,
            saved=saved)

    return render_template(
        "calculator/index.html",
        all_defaults=all_defaults)

@main_bp.route("/historial")
@login_required
def historial():
    analyses = (
        current_user.analyses
        .order_by(Analysis.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "history/index.html",
        analyses=analyses)


@main_bp.route("/historial/<int:analysis_id>", methods=["DELETE"])
@login_required
@limiter.limit("30 per minute")
def borrar_analisis(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)
    # Solo puede borrar el propietario
    if not analysis or analysis.user_id != current_user.id:
        return "", 404
    try:
        db.session.delete(analysis)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            "Error borrando análisis id=%s user_id=%s: %s",
            analysis_id, current_user.id, e, exc_info=True
        )
        flash(
            "No se pudo borrar el análisis. Inténtalo de nuevo.",
            "error"
        )
        # HTMX redirige al historial para mostrar el flash
        resp = make_response("", 200)   #Ya se manda el mensaje via flash
        resp.headers["HX-Redirect"] = url_for("main.historial")
        return resp
    return "", 200