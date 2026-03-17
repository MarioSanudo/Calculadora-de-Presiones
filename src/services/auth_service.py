import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app
from src.utils.extensions import db, bcrypt
from src.models.user import User


def hash_password(plain):
    return bcrypt.generate_password_hash(plain).decode("utf-8")


def check_password(hashed, plain):
    return bcrypt.check_password_hash(hashed, plain)


def create_user(username, surname, email, password):
    user = User(username=username, surname=surname, email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email, password):

    if not email:
        return None
        
    email_obtained=getattr(email,"data", email)  #Si viene de WTF-forms coge el data, si es string ya es data y no rompe
    clean_email=email_obtained.strip().lower()

    user = User.query.filter_by(email=clean_email).first()
    if user and check_password(user.password_hash, password):
        return user
    return None


def generate_jwt(user_id, expires_hours=1):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=expires_hours),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )


def decode_jwt(token):
    try:
        return jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
