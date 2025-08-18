from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, SelectMultipleField, FloatField
from wtforms.validators import Optional

class PumpSearchForm(FlaskForm):
    """Form for searching pump assemblies by duty point."""
    flow = FloatField('Flow Rate', validators=[Optional()])
    flow_units = SelectField('Flow Units', choices=[('l_per_s', 'L/s'), ('m3_per_h', 'm³/hr')], default='l_per_s')
    
    head = FloatField('Head', validators=[Optional()])
    head_units = SelectField('Head Units', choices=[('kpa', 'kPa'), ('m', 'm')], default='kpa')
    
    # This will be populated dynamically from the route
    pump_models = SelectMultipleField('Filter by Pump Models', coerce=str, validators=[Optional()])
    
    submit = SubmitField('Search')