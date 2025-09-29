from datetime import datetime
from . import db
from .user import User

class Resident(User):
    __tablename__ = "residents"
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey("streets.street_id"), nullable=False)
    
    # relationships
    street = db.relationship("Street", back_populates="residents")
    stop_requests = db.relationship("StopRequest", back_populates="resident", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="resident", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        'polymorphic_identity': 'resident',
    }
    
    def __init__(self, username, password, name, street, contact=None):
        super().__init__(username, password, name, contact)
        if street:
            self.street_id = street.street_id
            self.street = street
    
    def request_stop(self, route, quantity=1, notes=""):
        from .stop_request import StopRequest
        sr = StopRequest(route_id=route.route_id, resident_id=self.id, quantity=quantity, notes=notes)
        db.session.add(sr)
        db.session.commit()
        return sr
    
    def cancel_stop_request(self, stop_request):
        stop_request.status = "cancelled"
        db.session.commit()
    
    def view_driver_status_and_location(self, driver):
        return {"status": driver.status, "location": driver.location}
    
    def get_json(self):
        data = super().get_json()
        data.update({
            'street_id': self.street_id,
            'street_name': self.street.name if self.street else None
        })
        return data
    
    def __repr__(self):
        return f"<Resident id={self.id} name={self.name}>"