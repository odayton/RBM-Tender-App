# blueprints/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, FileField, SelectField, StringField, IntegerField,TextAreaField
from wtforms.validators import DataRequired, Optional

class CustomerForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    representative_name = StringField('Representative Name', validators=[DataRequired()])
    representative_email = StringField('Representative Email', validators=[DataRequired()])

class QuoteForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    company_id = SelectField('Company', coerce=int, validators=[DataRequired()])
    deal_location = StringField('Deal Location', validators=[Optional()])
    terms_conditions = TextAreaField('Terms and Conditions', validators=[Optional()])

class QuoteItemForm(FlaskForm):
    item_id = SelectField('Pump', coerce=int, validators=[DataRequired()])
    item_type = StringField('Item Type', default='Pump', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    total_price = FloatField('Total Price', validators=[DataRequired()])


class ManualUpdateForm(FlaskForm):
    table = SelectField('Table', choices=[
        ('Large_Seismic_Springs', 'Large Seismic Springs'),
        ('Additional_Price_Adders', 'Additional Price Adders'),
        ('Small_Seismic_Springs', 'Small Seismic Springs'),
        ('Inertia_Bases', 'Inertia Bases')
    ], validators=[DataRequired()])
    part_number = StringField('Part Number')
    name = StringField('Name')
    max_load_kg = FloatField('Max Load (kg)')
    static_deflection = FloatField('Static Deflection')
    spring_constant_kg_mm = FloatField('Spring Constant (kg/mm)')
    inner = StringField('Inner')
    outer = StringField('Outer')
    cost = FloatField('Cost')
    ip_adder = FloatField('IP Adder')
    drip_tray_adder = FloatField('Drip Tray Adder')
    length = FloatField('Length')
    width = FloatField('Width')
    height = FloatField('Height')
    spring_mount_height = FloatField('Spring Mount Height')
    spring_type = StringField('Spring Type')
    weight = FloatField('Weight')
    spring_qty = FloatField('Spring Quantity')
    spring_load = FloatField('Spring Load')
    file = FileField('File')

class SearchPumpsForm(FlaskForm):
    flow = FloatField('Flow (L/s)', validators=[Optional()])
    head = FloatField('Head', validators=[Optional()])
    head_unit = SelectField('Head Unit', choices=[('kpa', 'kPa'), ('m', 'm')], validators=[Optional()])
    poles = SelectField('Poles', choices=[('', 'Any'), ('2', '2P'), ('4', '4P')], validators=[Optional()])
    model_type = SelectField('Model Type', choices=[('', 'Any'), ('NBG', 'NBG'), ('CR', 'CR')], validators=[Optional()])
