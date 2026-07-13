import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError
from src.utils.extensions import db, bcrypt
from src.models.user import User
from src.routes.forms.auth_forms import _PASSWORD_REGEX, _PASSWORD_MSG, _NAME_MSG, _NAME_REGEX
import re, logging

logger= logging.getLogger(__name__)

def hash_password(plain):
    return bcrypt.generate_password_hash(plain).decode("utf-8")


def check_password(hashed, plain):
    return bcrypt.check_password_hash(hashed, plain)

def check_content_register(username, surname, email, password, confirmPassword):
    try:

        email, password = check_content_login(email, password)

        username=str(username)
        surname=str(surname)

        if not ( 2 <= len(username) <= 80):
            raise ValueError("La longitud del nombre no es la correcta")
        
        if not re.match(_NAME_REGEX, username) or not re.match(_NAME_REGEX, surname):
            raise ValueError(_NAME_MSG)
        
        if password != confirmPassword:
            raise ValueError("No coinciden las contraseñas")

    except TypeError:
        return None, None, None, None, None

    return username, surname, email, password, confirmPassword

def check_content_login(email, password):

    try:

        email=str(email).strip().lower()
        password=str(password)

        if "@" not in email or len(email) >= 254:
            raise ValueError("El formato del email no es correcto")
        
        if not password or not (8 <= len(password) <= 128):
            raise ValueError("No cumple la longitud adecuada de contraseña mínimo 8 caracter y máximo de 128, porfavor ajustese")
        
        if not re.match(_PASSWORD_REGEX, password):
            raise ValueError(_PASSWORD_MSG)
        
        
    except TypeError:
        return None, None #Directamente lo capturo y ni lo proceso, el otro error (ValueError) se captura en el endpoint, cuando haga la llamada a la función

    return email, password


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

    user = User.query.filter_by(email=clean_email).first()
    if user and check_password(user.password_hash, password):
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

    except jwt.InvalidAlgorithmError:
        logger.warning("Estan intentando modificar el token %s", token) #Prefiero poder ver el token para intentar sacar algo de posible info del atacante
        return None
    
    except jwt.DecodeError:
        logger.warning("Error en la decodificación del token %s\n, es probable que no este completo o este mal la codificación base 64")
        return None
    
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    
    if expected_purpose and payload.get("purpose") != expected_purpose:
        return None
    

    return payload
