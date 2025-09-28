from datetime import datetime
from models import db

class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.id'), nullable=False)

    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(32), default='scheduled', nullable=False)
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    driver = db.relationship('User', back_populates='routes')
    street = db.relationship('Street', back_populates='routes')
    stop_requests = db.relationship('StopRequest', back_populates='route', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='route', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Route id={self.id} driver_id={self.driver_id} street_id={self.street_id} scheduled={self.scheduled_time} status={self.status}>"
