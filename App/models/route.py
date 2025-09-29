from datetime import datetime
from . import db

class Route(db.Model):
    __tablename__ = "routes"
    
    route_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    street_id = db.Column(db.Integer, db.ForeignKey("streets.street_id"), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="scheduled")
    
    # relationships
    driver = db.relationship("Driver", back_populates="routes")
    street = db.relationship("Street", back_populates="routes")
    stop_requests = db.relationship("StopRequest", back_populates="route", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="route", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Route id={self.route_id} driver={self.driver_id} street={self.street_id} status={self.status}>"