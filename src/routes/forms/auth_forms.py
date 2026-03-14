from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp
)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Length(min=3, max=80),
        Regexp(
            r"^[a-zA-Z0-9_]+$",
            message="Solo letras, numeros y guion bajo."
        )
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
