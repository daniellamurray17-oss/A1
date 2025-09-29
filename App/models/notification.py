from datetime import datetime
from . import db

class Notification(db.Model):
    __tablename__ = "notifications"
    
    notification_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resident_id = db.Column(db.Integer, db.ForeignKey("residents.id"), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.route_id"), nullable=False)
    
    # relationships
    resident = db.relationship("Resident", back_populates="notifications")
    route = db.relationship("Route", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification id={self.notification_id} route={self.route_id} resident={self.resident_id}>"