from flask_wtf import FlaskForm
# Add FileRequired to this import statement
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    IntegerField,
    SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Email
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Company, User


def company_query():
    return Company.query

class PumpUploadForm(FlaskForm):
    """Form for uploading pump data"""
    file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Excel files only!')
    ])
    sheet_name = StringField('Sheet Name', validators=[Optional()])

class TechDataUploadForm(FlaskForm):
    """Form for uploading technical data"""
    file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF files only!')
    ])
    pump_type = SelectField('Pump Type', choices=[('NBG', 'NBG Series'), ('CR', 'CR Series'), ('TP', 'TP Series'), ('CM', 'CM Series'), ('MAGNA', 'Magna Series'), ('UPS', 'UPS Series'), ('CRE', 'CRE Series'), ('TPE', 'TPE Series'), ('NK', 'NK Series')], validators=[DataRequired()])

class ManageInertiaBasesForm(FlaskForm):
    """Form for managing inertia bases"""
    part_number = StringField('Part Number', validators=[DataRequired()])
    dimensions = StringField('Size', validators=[DataRequired()])
    weight_kg = DecimalField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])

class ManageSeismicSpringsForm(FlaskForm):
    """Form for managing seismic springs"""
    part_number = StringField('Part Number', validators=[DataRequired()])
    spring_rate_k = StringField('Spring Rate (k)', validators=[DataRequired()])
    max_deflection_mm = DecimalField('Max Deflection (mm)', validators=[DataRequired(), NumberRange(min=0)])
    
class ManageRubberMountsForm(FlaskForm):
    """Form for managing rubber mounts"""
    part_number = StringField('Part Number', validators=[DataRequired()])
    mount_type = StringField('Mount Type', validators=[DataRequired()])
    load_capacity_kg = DecimalField('Load Capacity (kg)', validators=[DataRequired(), NumberRange(min=0)])

class BOMUploadForm(FlaskForm):
    """Form for uploading BOM data"""
    file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Excel files only!')
    ])
    pump_series = SelectField('Pump Series', choices=[('NBG', 'NBG Series'), ('CR', 'CR Series'), ('TP', 'TP Series'), ('CM', 'CM Series')], validators=[DataRequired()])

class AdditionalPriceAdderForm(FlaskForm):
    """Form for managing additional price adders"""
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])

class ContactForm(FlaskForm):
    """Form for creating and editing contacts"""
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    position = StringField('Position/Title', validators=[Optional()])
    company = QuerySelectField('Company', query_factory=company_query, get_label='company_name', allow_blank=True)
    submit = SubmitField('Save Contact')

class DealOwnerForm(FlaskForm):
    """A simple form to create a new Deal Owner (User) for development."""
    username = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    submit = SubmitField('Create Deal Owner')

class CompanyForm(FlaskForm):
    """Form for creating a new Company"""
    company_name = StringField('Company Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[Optional()])
    submit = SubmitField('Create Company')