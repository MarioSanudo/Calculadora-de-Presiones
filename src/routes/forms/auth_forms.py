from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp)

# Solo letras (incluye tildes y ñ), sin espacios ni guiones
_NAME_REGEX = r"^[a-zA-ZÀ-ÿ]+$"
_NAME_MSG = "Solo letras, sin espacios ni guiones."

# Al menos una mayúscula y un carácter especial
_PASSWORD_REGEX = (
    r"^(?=.*[A-Z])(?=.*[!@#$%^&*()\-_=+\[\]{};':\"\\|,.<>/?¡¿]).*$"
)
_PASSWORD_MSG = (
    "Debe contener al menos una mayúscula y un carácter especial "
    "(!@#$%^&*¡¿, etc.)."
)


class RegistrationForm(FlaskForm):
    username = StringField("Nombre", validators=[
        DataRequired(),
        Length(min=2, max=80),
        Regexp(_NAME_REGEX, message=_NAME_MSG)
    ])
    surname = StringField("Apellido", validators=[
        DataRequired(),
        Length(min=2, max=80),
        Regexp(_NAME_REGEX, message=_NAME_MSG)
    ])
    email = StringField("Email", validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired(),
        Length(min=8, max=128),
        Regexp(_PASSWORD_REGEX, message=_PASSWORD_MSG)
    ])
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(),
            EqualTo("password", message="No coinciden las contraseñas.")
    ])
    submit = SubmitField("Registrarse")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired()
    ])
    submit = SubmitField("Iniciar sesión")


class ResendVerificationForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    submit = SubmitField("Reenviar verificación")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    submit = SubmitField("Enviar enlace")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Nueva contraseña",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(_PASSWORD_REGEX,message=_PASSWORD_MSG)
        ])

    confirm_password = PasswordField(
        "Confirmar",
        validators=[
            DataRequired(),
            EqualTo("password", message="No coinciden las contraseñas.")
        ])
    submit = SubmitField("Cambiar contraseña")
