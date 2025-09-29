from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=True)
    user_type = db.Column(db.String(20), nullable=False)  # 'driver' or 'resident'
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }
    
    def __init__(self, username, password, name, contact=None):
        self.username = username
        self.set_password(password)
        self.name = name
        self.contact = contact
    
    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'contact': self.contact,
            'user_type': self.user_type
        }
    
    def __repr__(self):
        return f'<User {self.id} - {self.username}>'