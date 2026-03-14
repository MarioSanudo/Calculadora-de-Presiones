from flask import Blueprint, render_template, redirect
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # En Fase 2 redirigirá a la calculadora si está autenticado
    return render_template("index.html")
