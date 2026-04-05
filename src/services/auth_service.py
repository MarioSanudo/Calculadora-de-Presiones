import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from src.utils.extensions import db, bcrypt
from src.models.user import User


def hash_password(plain):
    return bcrypt.generate_password_hash(plain).decode("utf-8")


def check_password(hashed, plain):
    return bcrypt.check_password_hash(hashed, plain)


def create_user(username, surname, email, password):
    if not password or not password.strip():
        raise ValueError("La contraseña no puede estar vacía.")
    email = email.strip().lower()
    try:
        user = User(
            username=username,
            surname=surname,
            email=email,
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def authenticate_user(email, password):

    if not email:
        return None

    email_obtained = getattr(email, "data", email)
    clean_email = email_obtained.strip().lower()

    _OAUTH_SENTINEL = "OAUTH_USER_NO_PASSWORD"  #Para los inicios de sesión con google el la password por defecto para no crearlo como nullable la columna password

    user = User.query.filter_by(email=clean_email).first()
    if (user and user.password_hash != _OAUTH_SENTINEL and check_password(user.password_hash, password) ):
        return user
    return None


def generate_jwt(user_id, purpose="general", expires_minutes=60):
    
    payload = {
        "user_id": user_id,
        "purpose": purpose,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )


def decode_jwt(token, expected_purpose=None):
    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    if expected_purpose and payload.get("purpose") != expected_purpose:
        return None

    return payload
