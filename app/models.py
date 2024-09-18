from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class AdditionalPriceAdders(db.Model):
    __tablename__ = 'AdditionalPriceAdders'
    id = db.Column(db.Integer, primary_key=True)
    IPAdder = db.Column(db.Float)
    DripTrayAdder = db.Column(db.Float)

class Companies(db.Model):
    __tablename__ = 'Companies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String)
    address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    contacts = db.relationship('Contacts', backref='company', lazy=True)
    deals = db.relationship('Deals', backref='company', lazy=True)

class Contacts(db.Model):
    __tablename__ = 'Contacts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    representative_name = db.Column(db.String)
    representative_email = db.Column(db.String)
    phone_number = db.Column(db.String)
    company_id = db.Column(db.Integer, db.ForeignKey('Companies.id'))
    deals = db.relationship('Deals', backref='contact', lazy=True)

class DealCompanies(db.Model):
    __tablename__ = 'DealCompanies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('Deals.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('Companies.id'))

class DealContacts(db.Model):
    __tablename__ = 'DealContacts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('Deals.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('Contacts.id'))

class DealOwners(db.Model):
    __tablename__ = 'DealOwners'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_name = db.Column(db.String)
    email = db.Column(db.String)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=func.now())

class Deals(db.Model):
    __tablename__ = 'Deals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    stage = db.Column(db.String)
    type = db.Column(db.String)
    location = db.Column(db.String)
    close_date = db.Column(db.DateTime)
    owner = db.Column(db.String)
    contact_id = db.Column(db.Integer, db.ForeignKey('Contacts.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('Companies.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    amount = db.Column(db.Float, default=0.0)
    revisions = db.relationship('Revisions', backref='deal', lazy=True)

class GeneralPumpDetails(db.Model):
    __tablename__ = 'GeneralPumpDetails'
    sku = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    poles = db.Column(db.Integer)
    kw = db.Column(db.Float)
    ie_class = db.Column(db.String)
    mei = db.Column(db.Float)
    weight = db.Column(db.Float)
    length = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    image_path = db.Column(db.String)

class HistoricPumpData(db.Model):
    __tablename__ = 'HistoricPumpData'
    id = db.Column(db.Integer, primary_key=True)  # Added primary key
    sku = db.Column(db.String)
    name = db.Column(db.String)
    flow = db.Column(db.Float)
    flow_unit = db.Column(db.String)
    head = db.Column(db.Float)
    head_unit = db.Column(db.String)
    efficiency = db.Column(db.String)
    absorbed_power = db.Column(db.String)
    npsh = db.Column(db.String)
    image_path = db.Column(db.String)
    link = db.Column(db.String)  # Added as requested for future use

class InertiaBases(db.Model):
    __tablename__ = 'InertiaBases'
    PartNumber = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    Length = db.Column(db.Float)
    Width = db.Column(db.Float)
    Height = db.Column(db.Float)
    Weight = db.Column(db.Float)
    SpringMountHeight = db.Column(db.Float)
    SpringQty = db.Column(db.Integer)
    SpringLoad = db.Column(db.Float)
    Cost = db.Column(db.Float)

class LargeSeismicSprings(db.Model):
    __tablename__ = 'LargeSeismicSprings'
    PartNumber = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    MaxLoad_kg = db.Column(db.Float)
    StaticDeflection = db.Column(db.Float)
    SpringConstant_kg_mm = db.Column(db.Float)
    Inner = db.Column(db.String)
    Outer = db.Column(db.String)
    Cost = db.Column(db.Float)

class Revisions(db.Model):
    __tablename__ = 'Revisions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('Deals.id'))
    version = db.Column(db.String)
    description = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

class RubberMounts(db.Model):
    __tablename__ = 'RubberMounts'
    PartNumber = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    Weight = db.Column(db.Float)
    Cost = db.Column(db.Float)

class SmallSeismicSprings(db.Model):
    __tablename__ = 'SmallSeismicSprings'
    PartNumber = db.Column(db.String, primary_key=True)
    Name = db.Column(db.String)
    MaxLoad_kg = db.Column(db.Float)
    StaticDeflection = db.Column(db.Float)
    SpringConstant_kg_mm = db.Column(db.Float)
    Stripe1 = db.Column(db.String)
    Stripe2 = db.Column(db.String)
    Cost = db.Column(db.Float)