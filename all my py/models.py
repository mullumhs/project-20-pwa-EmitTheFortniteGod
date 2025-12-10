from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserDrink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    raw_name = db.Column(db.String(255), nullable=False)
    matched_table = db.Column(db.String(20))   # beer/wine/spirit
    matched_id = db.Column(db.Integer)
    correction_status = db.Column(db.String(20))  # exact/corrected/None
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Beer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    brewery = db.Column(db.String(255))
    style = db.Column(db.String(100))
    abv = db.Column(db.Float)
    country = db.Column(db.String(100))
    strength = db.Column(db.String(10))   # "low", "mid", "high"
    notes = db.Column(db.Text)

class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    producer = db.Column(db.String(255))
    varietal = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    abv = db.Column(db.Float)
    sweetness = db.Column(db.String(20))
    vintage = db.Column(db.Integer)
    notes = db.Column(db.Text)

class Spirit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    brand = db.Column(db.String(255))
    category = db.Column(db.String(100))
    subtype = db.Column(db.String(100))
    abv = db.Column(db.Float)
    country = db.Column(db.String(100))
    flavor_notes = db.Column(db.Text)
    aging = db.Column(db.String(100))
