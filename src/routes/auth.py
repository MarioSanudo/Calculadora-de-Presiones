from flask import (Blueprint, render_template, redirect, url_for, flash, request)
from flask_login import (login_user, logout_user, login_required, current_user)
from src.utils.extensions import limiter
from src.routes.forms.auth_forms import (RegistrationForm, LoginForm)
from src.services.auth_service import (create_user, authenticate_user)
from src.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():
    if current_user.is_authenticated:
        return redirect("/")

    form = RegistrationForm()

    if form.validate_on_submit():
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash("Ese email ya esta registrado.", "error")
            return render_template("auth/register.html", form=form)

        existing_name = User.query.filter_by(
            username=form.username.data,
            surname=form.surname.data
        ).first()
        if existing_name:
            flash("Ese nombre y apellido ya estan registrados.", "error")
            return render_template("auth/register.html", form=form)

        create_user(username=form.username.data, surname=form.surname.data, email=form.email.data, password=form.password.data)
        flash("Cuenta creada. Inicia sesion.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(email=form.email.data,password=form.password.data)
        if user:
            login_user(user)
            next_page = request.args.get("next")
            flash("Sesion iniciada.", "success")
            return redirect(next_page or "/")

        flash("Email o contraseña incorrectos.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada.", "info")
    return redirect(url_for("auth.login"))
