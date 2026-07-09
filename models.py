from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)
    approval_status = db.Column(db.String(20), default="approved")
    blacklist_status = db.Column(db.Boolean, default=False)
    treks_guided = db.relationship("Trek", backref="guide", lazy=True)
    bookings = db.relationship("Booking", backref="trekker", lazy=True)
    
class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_title = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    remaining_slots = db.Column(db.Integer, nullable=False)
    current_status = db.Column(db.String(20), default="Open")
    description = db.Column(db.Text)
    guide_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    bookings = db.relationship("Booking", backref="trek", lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trekker_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    booked_on = db.Column(db.DateTime, default=datetime.utcnow)
    booking_status = db.Column(db.String(20), default="Confirmed")
