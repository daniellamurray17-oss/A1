from datetime import datetime
from models import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    route = db.relationship('Route', back_populates='notifications')

    def __repr__(self):
        return f"<Notification id={self.id} route_id={self.route_id} is_read={self.is_read}>"
