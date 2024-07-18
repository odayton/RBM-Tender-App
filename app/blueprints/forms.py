from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, FileField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Email, NumberRange

class CustomerForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    representative_name = StringField('Representative Name', validators=[DataRequired()])
    representative_email = StringField('Representative Email', validators=[DataRequired(), Email()])

class QuoteForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    company_id = SelectField('Company', coerce=int, validators=[DataRequired()])
    deal_location = StringField('Deal Location', validators=[Optional()])
    terms_conditions = TextAreaField('Terms and Conditions', validators=[Optional()])

class QuoteItemForm(FlaskForm):
    item_id = SelectField('Pump', coerce=int, validators=[DataRequired()])
    item_type = StringField('Item Type', default='Pump', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    total_price = FloatField('Total Price', validators=[DataRequired(), NumberRange(min=0)])

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
