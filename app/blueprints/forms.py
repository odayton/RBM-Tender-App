# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, FileField, SelectField, IntegerField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Email, NumberRange

class DealForm(FlaskForm):
    deal_name = StringField('Deal Name', validators=[DataRequired()])
    deal_stage = SelectField('Deal Stage', choices=[
        ('Sales Lead', 'Sales Lead'),
        ('Tender', 'Tender'),
        ('Proposal', 'Proposal'),
        ('Negotiation', 'Negotiation'),
        ('Closed Won', 'Closed Won'),
        ('Closed Lost', 'Closed Lost'),
        ('Abandoned', 'Abandoned')
    ], validators=[DataRequired()])
    deal_type = SelectField('Deal Type', choices=[
        ('HVAC Mechanical', 'HVAC Mechanical'),
        ('Hydraulic', 'Hydraulic'),
        ('OEM', 'OEM'),
        ('Wholesaler', 'Wholesaler'),
        ('Merchant', 'Merchant')
    ], validators=[DataRequired()])
    deal_location = SelectField('Deal Location', choices=[
        ('Queensland', 'Queensland'),
        ('New South Wales', 'New South Wales'),
        ('Victoria', 'Victoria'),
        ('Australian Capital Territory', 'Australian Capital Territory'),
        ('Western Australia', 'Western Australia'),
        ('Northern Territory', 'Northern Territory'),
        ('Tasmania', 'Tasmania')
    ], validators=[DataRequired()])
    close_date = DateField('Close Date', validators=[DataRequired()])
    deal_owner = SelectField('Deal Owner', choices=[], validators=[Optional()])
    contact_id = SelectField('Contact', choices=[], validators=[Optional()])
    company_id = SelectField('Company', choices=[], validators=[Optional()])
    contacts = SelectMultipleField('Contacts', choices=[], validators=[Optional()])
    companies = SelectMultipleField('Companies', choices=[], validators=[Optional()])
    submit = SubmitField('Save Changes')

class ContactForm(FlaskForm):
    representative_name = StringField('Representative Name', validators=[DataRequired()])
    representative_email = StringField('Representative Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    company_id = SelectField('Company', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class DealOwnerForm(FlaskForm):
    owner_name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Create Deal Owner')

class CompanyForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Create Company')

class ManualUpdateForm(FlaskForm):
    table = SelectField('Table', choices=[
        ('Large_Seismic_Springs', 'Large Seismic Springs'),
        ('Additional_Price_Adders', 'Additional Price Adders'),
        ('Small_Seismic_Springs', 'Small Seismic Springs'),
        ('Inertia_Bases', 'Inertia Bases')
    ], validators=[DataRequired()])
    part_number = StringField('Part Number')
    name = StringField('Name')
    max_load_kg = FloatField('Max Load (kg)', validators=[Optional(), NumberRange(min=0)])
    static_deflection = FloatField('Static Deflection', validators=[Optional(), NumberRange(min=0)])
    spring_constant_kg_mm = FloatField('Spring Constant (kg/mm)', validators=[Optional(), NumberRange(min=0)])
    inner = StringField('Inner', validators=[Optional()])
    outer = StringField('Outer', validators=[Optional()])
    cost = FloatField('Cost', validators=[Optional(), NumberRange(min=0)])
    ip_adder = FloatField('IP Adder', validators=[Optional(), NumberRange(min=0)])
    drip_tray_adder = FloatField('Drip Tray Adder', validators=[Optional(), NumberRange(min=0)])
    length = FloatField('Length', validators=[Optional(), NumberRange(min=0)])
    width = FloatField('Width', validators=[Optional(), NumberRange(min=0)])
    height = FloatField('Height', validators=[Optional(), NumberRange(min=0)])
    spring_mount_height = FloatField('Spring Mount Height', validators=[Optional(), NumberRange(min=0)])
    spring_type = StringField('Spring Type', validators=[Optional()])
    weight = FloatField('Weight', validators=[Optional(), NumberRange(min=0)])
    spring_qty = IntegerField('Spring Quantity', validators=[Optional(), NumberRange(min=0)])
    spring_load = FloatField('Spring Load', validators=[Optional(), NumberRange(min=0)])
    file = FileField('File', validators=[Optional()])

class SearchPumpsForm(FlaskForm):
    flow = FloatField('Flow (L/s)', validators=[Optional(), NumberRange(min=0)])
    head = FloatField('Head', validators=[Optional(), NumberRange(min=0)])
    head_unit = SelectField('Head Unit', choices=[('kpa', 'kPa'), ('m', 'm')], validators=[Optional()])
    poles = SelectField('Poles', choices=[('', 'Any'), ('2', '2P'), ('4', '4P')], validators=[Optional()])
    model_type = SelectField('Model Type', choices=[('', 'Any'), ('NBG', 'NBG'), ('CR', 'CR')], validators=[Optional()])

class BlankTechDataUploadForm(FlaskForm):
    file = FileField('Upload PDF File(s)', validators=[Optional()])
    zip_file = FileField('Upload ZIP File', validators=[Optional()])
    submit = SubmitField('Upload')

class HistoricTechDataUploadForm(FlaskForm):
    file = FileField('Upload PDF File(s)', validators=[Optional()])
    zip_file = FileField('Upload ZIP File', validators=[Optional()])
    submit = SubmitField('Upload')

class CSRFForm(FlaskForm):  # Add this class
    submit = SubmitField('Submit')

class InertiaBaseForm(FlaskForm):
    part_number = StringField('Part Number', validators=[DataRequired()])
    length = FloatField('Length', validators=[DataRequired()])
    width = FloatField('Width', validators=[DataRequired()])
    height = FloatField('Height', validators=[DataRequired()])
    spring_mount_height = FloatField('Spring Mount Height', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[DataRequired()])
    spring_amount = IntegerField('Spring Amount', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RubberMountForm(FlaskForm):
    part_number = StringField('Part Number', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SeismicSpringForm(FlaskForm):
    part_number = StringField('Part Number', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    max_load_kg = FloatField('Max Load (kg)', validators=[DataRequired()])
    static_deflection = FloatField('Static Deflection', validators=[DataRequired()])
    spring_constant_kg_mm = FloatField('Spring Constant (kg/mm)', validators=[DataRequired()])
    stripe1 = StringField('Stripe 1', validators=[Optional()])
    stripe2 = StringField('Stripe 2', validators=[Optional()])
    cost = FloatField('Cost', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AdditionalPriceAdderForm(FlaskForm):
    ip_adder = FloatField('IP Adder', validators=[DataRequired()])
    drip_tray_adder = FloatField('Drip Tray Adder', validators=[DataRequired()])
    submit = SubmitField('Submit')

class FileUploadForm(FlaskForm):
    file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Excel files only!')
    ])
    submit = SubmitField('Upload')