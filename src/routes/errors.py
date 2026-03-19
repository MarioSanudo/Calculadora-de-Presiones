from flask import Blueprint, render_template, redirect
from flask_wtf.csrf import CSRFError

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(429)
def too_many_requests(e):
    return render_template("errors/429.html"), 429


@errors_bp.app_errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


@errors_bp.app_errorhandler(CSRFError)
def csrf_error(e):
    # Redirige al inicio; el token expirado ya invalida el form
    return redirect("/"), 303
