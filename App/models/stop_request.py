from datetime import datetime
from . import db

class StopRequest(db.Model):
    __tablename__ = "stop_requests"
    
    request_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default="requested")
    route_id = db.Column(db.Integer, db.ForeignKey("routes.route_id"), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey("residents.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationships
    resident = db.relationship("Resident", back_populates="stop_requests")
    route = db.relationship("Route", back_populates="stop_requests")
    
    def __repr__(self):
        return f"<StopRequest id={self.request_id} route={self.route_id} resident={self.resident_id}>"