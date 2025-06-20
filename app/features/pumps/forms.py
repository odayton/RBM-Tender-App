from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    SelectField,
    FileField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileRequired, FileAllowed

class PumpForm(FlaskForm):
    """
    Form for adding or editing a pump model.
    """
    pump_model = StringField('Pump Model', validators=[DataRequired()])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    submit = SubmitField('Add Pump')

class PumpSearchForm(FlaskForm):
    """Form for searching pumps"""
    flow_rate = FloatField(
        'Flow Rate (m³/h)',
        validators=[
            DataRequired(message="Flow rate is required"),
            NumberRange(min=0, message="Flow rate must be positive")
        ]
    )
    
    head = FloatField(
        'Head (m)',
        validators=[
            DataRequired(message="Head is required"),
            NumberRange(min=0, message="Head must be positive")
        ]
    )

class TechDataUploadForm(FlaskForm):
    """Form for uploading pump technical data"""
    file = FileField(
        'PDF File',
        validators=[
            FileRequired(),
            FileAllowed(['pdf'], 'PDF files only!')
        ]
    )
    
    pump_series = SelectField(
        'Pump Series',
        choices=[
            ('NBG', 'NBG Series'),
            ('CR', 'CR Series'),
            ('TP', 'TP Series'),
            ('CM', 'CM Series'),
            ('MAGNA', 'Magna Series'),
            ('UPS', 'UPS Series'),
            ('CRE', 'CRE Series'),
            ('TPE', 'TPE Series'),
            ('NK', 'NK Series')
        ],
        validators=[DataRequired()]
    )
    
    notes = TextAreaField(
        'Notes',
        validators=[Optional()]
    )

class PumpManualUpdateForm(FlaskForm):
    """Form for manually updating pump data"""
    sku = StringField(
        'SKU',
        validators=[DataRequired()]
    )
    
    power_kw = FloatField(
        'Power (kW)',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Power must be positive")
        ]
    )
    
    flow_rate = FloatField(
        'Flow Rate (m³/h)',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Flow rate must be positive")
        ]
    )
    
    head = FloatField(
        'Head (m)',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Head must be positive")
        ]
    )
    
    efficiency = FloatField(
        'Efficiency (%)',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="Efficiency must be between 0 and 100")
        ]
    )
    
    ie_class = SelectField(
        'IE Class',
        choices=[
            ('IE1', 'IE1'),
            ('IE2', 'IE2'),
            ('IE3', 'IE3'),
            ('IE4', 'IE4')
        ],
        validators=[Optional()]
    )

class HistoricPumpSearchForm(FlaskForm):
    """Form for searching historic pump selections"""
    min_flow = FloatField(
        'Min Flow Rate (m³/h)',
        validators=[Optional()]
    )
    
    max_flow = FloatField(
        'Max Flow Rate (m³/h)',
        validators=[Optional()]
    )
    
    min_head = FloatField(
        'Min Head (m)',
        validators=[Optional()]
    )
    
    max_head = FloatField(
        'Max Head (m)',
        validators=[Optional()]
    )
    
    pump_series = SelectField(
        'Pump Series',
        choices=[
            ('', 'All'),
            ('NBG', 'NBG Series'),
            ('CR', 'CR Series'),
            ('TP', 'TP Series'),
            ('CM', 'CM Series'),
            ('MAGNA', 'Magna Series'),
            ('UPS', 'UPS Series'),
            ('CRE', 'CRE Series'),
            ('TPE', 'TPE Series'),
            ('NK', 'NK Series')
        ],
        validators=[Optional()]
    )

    def validate(self):
        """Custom validation for range fields"""
        if not super().validate():
            return False
            
        if self.min_flow.data and self.max_flow.data:
            if self.min_flow.data > self.max_flow.data:
                self.min_flow.errors.append("Min flow cannot be greater than max flow")
                return False
                
        if self.min_head.data and self.max_head.data:
            if self.min_head.data > self.max_head.data:
                self.min_head.errors.append("Min head cannot be greater than max head")
                return False
                
        return True