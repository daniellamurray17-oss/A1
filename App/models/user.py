from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'driver' or 'resident'
    contact = db.Column(db.String(120), nullable=True)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.id'), nullable=True)

    street = db.relationship('Street', back_populates='residents')
    routes = db.relationship('Route', back_populates='driver', cascade='all, delete-orphan')
    stop_requests = db.relationship('StopRequest', back_populates='resident', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='resident', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_driver(self):
        return self.role == 'driver'

    def is_resident(self):
        return self.role == 'resident'

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"
