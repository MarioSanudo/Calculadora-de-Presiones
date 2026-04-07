from src.utils.extensions import db
from datetime import datetime, timezone


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Parámetros de entrada
    rider_weight = db.Column(db.Float, nullable=False)
    bike_weight = db.Column(db.Float, nullable=False)
    tire_width_front = db.Column(db.Float, nullable=False)
    tire_width_rear = db.Column(db.Float, nullable=False)
    inner_rim_width = db.Column(db.Float, nullable=False)
    wheel_diameter = db.Column(db.Integer, nullable=False)
    tire_casing = db.Column(db.String(50), nullable=False)
    ride_style = db.Column(db.String(50), nullable=False)
    rim_type = db.Column(db.String(50), nullable=False)
    surface = db.Column(db.String(50), nullable=False)

    # Resultados del cálculo
    front_bar = db.Column(db.Float, nullable=False)
    front_psi = db.Column(db.Float, nullable=False)
    rear_bar = db.Column(db.Float, nullable=False)
    rear_psi = db.Column(db.Float, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc))

    # Relación con User (lado N del 1:M)
    user = db.relationship("User", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis {self.id} user={self.user_id}>"
