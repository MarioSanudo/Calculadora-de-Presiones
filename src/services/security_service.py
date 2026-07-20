# app/security.py
from flask import session, redirect, flash, url_for
from flask_login import current_user, logout_user

def register_security_hooks(app):
    @app.before_request #Toda la aplicación, no blueprints para que así en cualquier endpoint haga esta comprobación
    def check_session_version():
        if current_user.is_authenticated:
            if session.get('session_version') != current_user.session_version:
                logout_user()
                flash("Por motivos de seguridad, vuelva a iniciar sesión por favor", category="info")
                return redirect(url_for("auth.login"))