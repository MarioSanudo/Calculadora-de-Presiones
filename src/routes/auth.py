import logging
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.utils.extensions import db, limiter, oauth
from src.utils.validators import validar_next
from src.routes.forms.auth_forms import (
    RegistrationForm, LoginForm,
    ResendVerificationForm, ForgotPasswordForm,
    ResetPasswordForm
)
from src.services.auth_service import (
    create_user, authenticate_user,
    decode_jwt, hash_password
)
from src.services.email_service import (
    send_verification_email,
    send_password_reset_email
)
from src.models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Register ────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect("/")

    form = RegistrationForm()

    if form.validate_on_submit():
        existing_email = User.query.filter_by(
            email=form.email.data.strip().lower()
        ).first()
        if existing_email:
            flash("Ese email ya esta registrado.", "error")
            return render_template(
                "auth/register.html", form=form
            )

        username = form.username.data
        if User.query.filter_by(
            username=username,
            surname=form.surname.data
        ).first():
            count = User.query.filter_by(username=username).count()
            username = f"{username}{count + 1}"

        try:
            user = create_user(
                username=username,
                surname=form.surname.data,
                email=form.email.data,
                password=form.password.data
            )
        except ValueError as e:
            flash(str(e), "error")
            return render_template(
                "auth/register.html", form=form
            )
        except SQLAlchemyError:
            logger.exception(
                f"Error al crear usuario email={form.email.data}"
            )
            flash(
                "Error al crear la cuenta. Intentalo de nuevo.",
                "error"
            )
            return render_template(
                "auth/register.html", form=form
            )

        try:
            send_verification_email(user)
        except Exception:
            logger.exception(
                "Error al enviar email de verificación "
                "a %s", user.email
            )

        flash(
            "Cuenta creada. Revisa tu email para verificar tienes 24h.",
            "success"
        )
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html", form=form
    )


# ── Login ───────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(
            email=form.email.data,
            password=form.password.data
        )
        if user:
            if not user.is_verified:
                try:
                    send_verification_email(user)
                except Exception:
                    logger.exception(
                        "Error reenviando verificación en login a %s",
                        user.email
                    )
                flash(
                    "Email no verificado. Revisa tu email para verificar tienes 24h.",
                    "info"
                )
                return render_template(
                    "auth/login.html", form=form
                )

            login_user(user)
            next_raw = request.args.get("next")
            next_page = (
                validar_next(next_raw)
                if next_raw else None
            )
            flash("Sesión iniciada.", "success")
            return redirect(
                next_page if next_page else "/"
            )

        flash("Email o contraseña incorrectos.", "error")

    return render_template(
        "auth/login.html", form=form
    )


# ── Logout ──────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))


# ── Email verification ──────────────────────────────

@auth_bp.route("/verify/<token>")
@limiter.limit("10 per minute")
def verify_email(token):
    payload = decode_jwt(
        token, expected_purpose="email_verification"    #Con purpose limito de donde venga el el token, para evitar robos y que lo peguen en la url
    )
    if not payload:
        flash(
            "Enlace invalido o expirado.",
            "error"
        )
        return redirect(url_for("auth.login"))

    user = db.session.get(User, payload["user_id"])
    if not user:
        # Token válido pero user_id inexistente — posible manipulación
        logger.warning(
            "verify_email: token válido con user_id inexistente user_id=%s",
            payload["user_id"]
        )
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("auth.login"))

    if user.is_verified:
        flash("Tu cuenta ya esta verificada.", "info")
        return redirect(url_for("auth.login"))

    try:
        user.is_verified = True
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(
            "Error verificando email user_id=%s",
            payload["user_id"]
        )
        flash(
            "Error al verificar el email. Intentalo de nuevo.",
            "error"
        )
        return redirect(url_for("auth.login"))

    flash("Email verificado. Ya puedes iniciar sesión.",
          "success")
    return redirect(url_for("auth.login"))


@auth_bp.route(
    "/resend-verification", methods=["GET", "POST"]
)
@limiter.limit("5 per minute")
def resend_verification():
    form = ResendVerificationForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.strip().lower()
        ).first()

        if user:
            if user.is_verified:
                flash(
                    "Tu cuenta ya esta verificada. Por favor inicia sesión.",
                    "info"
                )
            else:
                try:
                    send_verification_email(user)
                except Exception:
                    logger.exception(
                        "Error reenviando verificación a %s",
                        user.email
                    )
                flash(
                    "Email de verificación enviado. Revisa tu bandeja de entrada.",
                    "info"
                )
        else:
            # No revelamos si el email existe o no
            flash(
                "Si el email existe, se ha enviado un enlace.",
                "info"
            )
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/resend_verification.html", form=form
    )


# ── Password reset ──────────────────────────────────

@auth_bp.route(
    "/forgot-password", methods=["GET", "POST"]
)
@limiter.limit("5 per minute")
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.strip().lower()
        ).first()

        if user and user.is_verified:
            try:
                send_password_reset_email(user)
            except Exception:
                logger.exception(
                    "Error enviando reset a %s",
                    user.email
                )

        flash(
            "Si el email existe, recibirás un enlace para cambiar tu contraseña.",
            "info"
        )
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/forgot_password.html", form=form
    )


@auth_bp.route(
    "/reset-password/<token>", methods=["GET", "POST"]
)
@limiter.limit("5 per minute")
def reset_password(token):
    payload = decode_jwt(
        token, expected_purpose="password_reset"
    )
    if not payload:
        flash(
            "Enlace inválido o expirado.",
            "error"
        )
        return redirect(url_for("auth.forgot_password"))

    user = db.session.get(User, payload["user_id"])
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        try:
            user.password_hash = hash_password(
                form.password.data
            )
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception(
                "Error reseteando contraseña user_id=%s",
                payload["user_id"]
            )
            flash(
                "Error al cambiar la contraseña, intentalo de nuevo.",
                "error"
            )
            return render_template(
                "auth/reset_password.html",
                form=form,
                token=token
            )
        flash(
            "Contraseña cambiada. Inicia sesión.",
            "success"
        )
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password.html",
        form=form,
        token=token
    )


# ── Google OAuth ────────────────────────────────────

@auth_bp.route("/login/google")
def google_login():
    redirect_uri = url_for(
        "auth.google_callback", _external=True
    )
    return oauth.google.authorize_redirect(
        redirect_uri
    )


@auth_bp.route("/login/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception:
        logger.exception("Error en Google OAuth callback")
        flash(
            "Error al iniciar sesion con Google.",
            "error"
        )
        return redirect(url_for("auth.login"))

    userinfo = token.get("userinfo")
    if not userinfo:
        flash(
            "No se pudo obtener información de Google.",
            "error"
        )
        return redirect(url_for("auth.login"))

    google_id = userinfo["sub"] #Id único del usuario
    email = userinfo["email"].strip().lower()
    name = userinfo.get("given_name", "Usuario")    #Con fallback (Usuario)
    surname = userinfo.get("family_name", "Google")

    # Caso 1: usuario ya vinculado con Google
    user = User.query.filter_by(
        google_id=google_id
    ).first()
    if user:
        login_user(user)
        flash("Sesión iniciada con Google.", "success")
        return redirect("/")

    # Caso 2: email existe sin google_id → vincular
    user = User.query.filter_by(email=email).first()
    if user:
        user.google_id = google_id
        user.is_verified = True
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception(
                "Error vinculando google_id a user email=%s",
                email
            )
            flash(
                "Error al vincular la cuenta. Intentalo de nuevo.",
                "error"
            )
            return redirect(url_for("auth.login"))
        login_user(user)
        flash("Cuenta vinculada con Google.", "success")
        return redirect("/")

    # Caso 3: usuario nuevo
    user = User(
        username=name,
        surname=surname,
        email=email,
        google_id=google_id,
        is_verified=True,
        password_hash="OAUTH_USER_NO_PASSWORD"  #Contraseña genérica no me hace falta encriptarla
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Colision username+surname → sufijo numerico
        count = User.query.filter_by(
            username=name
        ).count()
        user = User(
            username=f"{name}{count + 1}",
            surname=surname,
            email=email,
            google_id=google_id,
            is_verified=True,
            password_hash="OAUTH_USER_NO_PASSWORD"
        )
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception(
                "Error creando usuario OAuth google_id=%s",
                google_id
            )
            flash(
                "Error al crear la cuenta. Intentalo de nuevo.",
                "error"
            )
            return redirect(url_for("auth.login"))

    login_user(user)
    flash("Cuenta creada con Google.", "success")
    return redirect("/")
