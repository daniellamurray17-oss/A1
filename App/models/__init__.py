from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from App.models.user import User
from App.models.street import Street
from App.models.route import Route
from App.models.stop_request import StopRequest
from App.models.notification import Notification

__all__ = [
    "db",
    "User",
    "Street",
    "Route",
    "StopRequest",
    "Notification"
]
