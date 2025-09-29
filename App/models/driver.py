from datetime import datetime
from . import db
from .user import User

class Driver(User):
    __tablename__ = "drivers"
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.String(50), default="available")
    location = db.Column(db.String(200), nullable=True)
    
    # relationships
    routes = db.relationship("Route", back_populates="driver", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        'polymorphic_identity': 'driver',
    }
    
    def __init__(self, username, password, name, contact=None, status="available", location=None):
        super().__init__(username, password, name, contact)
        self.status = status
        self.location = location
    
    def schedule_drive(self, street, scheduled_time):
        from .route import Route
        route = Route(driver_id=self.id, street_id=street.street_id, scheduled_time=scheduled_time)
        db.session.add(route)
        db.session.commit()
        return route
    
    def update_status(self, status):
        self.status = status
        db.session.commit()
    
    def update_location(self, location):
        self.location = location
        db.session.commit()
    
    def cancel_route(self, route):
        db.session.delete(route)
        db.session.commit()
    
    def get_json(self):
        data = super().get_json()
        data.update({
            'status': self.status,
            'location': self.location
        })
        return data
    
    def __repr__(self):
        return f"<Driver id={self.id} name={self.name}>"