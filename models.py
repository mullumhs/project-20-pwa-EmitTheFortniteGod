from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserDrink(db.Model):
    __tablename__ = 'user_drinks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    raw_name = db.Column(db.String(255), nullable=False)
    matched_table = db.Column(db.String(20))   # 'beer' | 'wine' | 'spirit' | None
    matched_id = db.Column(db.Integer)         # catalog id if matched
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Catalog tables

class Beer(db.Model):
    __tablename__ = 'beers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    brewery = db.Column(db.String(255))
    style = db.Column(db.String(100))
    abv = db.Column(db.Float)
    country = db.Column(db.String(100))
    mid_strength = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

class Wine(db.Model):
    __tablename__ = 'wines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    producer = db.Column(db.String(255))
    varietal = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    abv = db.Column(db.Float)
    sweetness = db.Column(db.String(20))  # dry, medium, sweet
    vintage = db.Column(db.Integer)
    notes = db.Column(db.Text)

class Spirit(db.Model):
    __tablename__ = 'spirits'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    brand = db.Column(db.String(255))
    category = db.Column(db.String(100))  # gin, whisky, rum, tequila, vodka, liqueur, etc.
    subtype = db.Column(db.String(100))   # e.g., single malt, reposado, London Dry
    abv = db.Column(db.Float)
    country = db.Column(db.String(100))
    flavor_notes = db.Column(db.Text)
    aging = db.Column(db.String(100))
