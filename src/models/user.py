from src.utils.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates
from uuid import uuid4


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column( db.String(80), unique=False, nullable=False, index=True)
    surname=db.Column(db.String(80), unique= False, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(
        db.Boolean, default=False, nullable=False)
    google_id = db.Column(
        db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active_user = db.Column(db.Boolean, default=True)    #Puede ser útil para banear cuentas
    alternative_id=db.Column(db.String(128), nullable=False, unique=True, default=lambda:str(uuid4()))  #Id más seguro para las cookies


    # Historial de análisis del usuario (1:N)
    analyses = db.relationship(
        "Analysis", back_populates="user", lazy="dynamic")

    __table_args__=(
        UniqueConstraint("username", "surname", name="UsernameSurname_uix"),
    )

    @validates("email")
    def normalize_email(self, key, value):
        return value.strip().lower() if value else value

    def __repr__(self):
        return f"<User {self.username}>"
    
    
    def get_id(self):   #Se carga y da el id, cuando hay un login, load_user se activa
        return str(self.alternative_id)  # Cookie de sesión usa el UUID, no el PK
