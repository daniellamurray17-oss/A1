from . import db

class Street(db.Model):
    __tablename__ = "streets"
    
    street_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # relationships
    residents = db.relationship("Resident", back_populates="street", cascade="all, delete-orphan")
    routes = db.relationship("Route", back_populates="street", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Street id={self.street_id} name={self.name}>"