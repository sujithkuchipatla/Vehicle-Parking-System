# /models/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- USER MODEL ---
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Plain text (change to hashed in production)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    role = db.Column(db.String(10), default='user')  # 'user' or 'admin'

    # Relationship: One user can make many reservations
    reservations = db.relationship('ReserveSpot', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


# --- PARKING LOT MODEL ---
class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    max_spots = db.Column(db.Integer, nullable=False)

    # Relationship: One parking lot has many spots
    spots = db.relationship('ParkingSpot', back_populates='parking_lot', lazy=True)

    @property
    def used_spots(self):
        return sum(1 for spot in self.spots if spot.status == 'O')

    def __repr__(self):
        return f'<Lot {self.prime_location_name}>'


# --- PARKING SPOT MODEL ---
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  # A = Available, O = Occupied

    # Relationship: One spot can have many reservations
    reservations = db.relationship('ReserveSpot', backref='spot', lazy=True)

    parking_lot = db.relationship("ParkingLot", back_populates="spots")
    def __repr__(self):
        return f'<Spot {self.id} in Lot {self.lot_id} | Status: {self.status}>'


# --- RESERVATION MODEL ---
class ReserveSpot(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_no = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.id} | Spot {self.spot_id} | User {self.user_id}>'


# --- INITIALIZE ADMIN USER ---
def initialize_admin():
    from app import db  # prevent circular import

    existing_admin = User.query.filter_by(role='admin').first()
    
    if not existing_admin:
        admin_user = User(
            email='admin@gmail.com',
            password='admin',  # plain text (use hashed in real app)
            name='Admin',
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
