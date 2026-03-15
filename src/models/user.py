from src.utils.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column( db.String(80), unique=False, nullable=False, index=True)
    surname=db.Column(db.String(80), unique= False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active_user = db.Column(db.Boolean, default=True)

    __table_args__=(
        UniqueConstraint("username", "surname", name="UsernameSurname_uix"),
    )

    def __repr__(self):
        return f"<User {self.username}>"
