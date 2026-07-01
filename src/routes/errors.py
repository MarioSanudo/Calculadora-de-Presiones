import logging
from flask import Blueprint, render_template, redirect, request
from flask_wtf.csrf import CSRFError

errors_bp = Blueprint("errors", __name__)
logger = logging.getLogger(__name__)


@errors_bp.app_errorhandler(404)
def not_found(e):   #No es viable que haya un 404 en la petición de HTMX
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(429)
def too_many_requests(e):
    logger.error("Error 429 Muchas Peticiones: %s", e)

    if request.headers.get("HX-Request"):   #Si la petición viene de htmx para poder devolver fragmento
        return render_template("errors/fragment429.html")
        
    return render_template("errors/429.html"), 429


@errors_bp.app_errorhandler(500)
def server_error(e):
    logger.error("Error 500: %s", e)

    if request.headers.get("HX-Request"):
        return render_template("errors/fragment500.html"), 500
    
    return render_template("errors/500.html"), 500


@errors_bp.app_errorhandler(CSRFError)
def csrf_error(e):
    # Redirige al inicio; el token expirado ya invalida el form
    logger.warning("Hay usuarios tratando de saltarse el formulario %s", e)
    return redirect("/"), 303
