from App.models import db

class Street(db.Model):
    __tablename__ = 'streets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    residents = db.relationship('User', back_populates='street', lazy='dynamic')
    routes = db.relationship('Route', back_populates='street', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Street id={self.id} name={self.name}>"
