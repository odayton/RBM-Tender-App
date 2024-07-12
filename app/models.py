# app/models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PumpDetail(db.Model):
    __tablename__ = 'Pump_Details'
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    max_load_kg = db.Column(db.Float, nullable=False)
    static_deflection = db.Column(db.Float, nullable=False)
    spring_constant_kg_mm = db.Column(db.Float, nullable=False)
    inner = db.Column(db.String(64))
    outer = db.Column(db.String(64))
    cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HistoricalSelection(db.Model):
    __tablename__ = 'Historical_Selections'
    id = db.Column(db.Integer, primary_key=True)
    pump_id = db.Column(db.Integer, db.ForeignKey('Pump_Details.id'), nullable=False)
    flow = db.Column(db.Float, nullable=False)
    head = db.Column(db.Float, nullable=False)
    power_absorbed = db.Column(db.Float)
    npsh = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quote(db.Model):
    __tablename__ = 'Quotes'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(128), nullable=False)
    customer_name = db.Column(db.String(128), nullable=False)
    reference_number = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuoteItem(db.Model):
    __tablename__ = 'Quote_Items'
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('Quotes.id'), nullable=False)
    pump_id = db.Column(db.Integer, db.ForeignKey('Pump_Details.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

