from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp
)

# Acepta letras (incluye tildes y ñ), espacios y guiones
_NAME_REGEX = r"^[a-zA-ZÀ-ÿ]+([\s\-'][a-zA-ZÀ-ÿ]+)*$"
_NAME_MSG = "Solo letras, puede incluir espacios o guiones."


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
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="No coinciden.")
        ]
    )
    submit = SubmitField("Registrarse")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField("Password", validators=[
        DataRequired()
    ])
    submit = SubmitField("Iniciar sesion")
