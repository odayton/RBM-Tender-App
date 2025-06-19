from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    TextAreaField, 
    DecimalField, 
    SelectField,
    DateTimeField,
    FileField
)
from wtforms.validators import DataRequired, Optional, Email, ValidationError
from app.models.deals.deal_quote_model import DealType, AustralianState, DealStage

class SearchForm(FlaskForm):
    """Base search form"""
    query = StringField('Search', validators=[Optional()])
    sort_by = SelectField(
        'Sort By',
        choices=[
            ('date_desc', 'Newest First'),
            ('date_asc', 'Oldest First'),
            ('name_asc', 'Name A-Z'),
            ('name_desc', 'Name Z-A')
        ],
        default='date_desc'
    )

class DealSearchForm(SearchForm):
    """Form for searching deals"""
    deal_type = SelectField(
        'Deal Type',
        choices=[(type.name, type.value) for type in DealType],
        validators=[Optional()]
    )
    
    state = SelectField(
        'State',
        choices=[(state.name, state.value) for state in AustralianState],
        validators=[Optional()]
    )
    
    stage = SelectField(
        'Stage',
        choices=[(stage.name, stage.value) for stage in DealStage],
        validators=[Optional()]
    )

class CustomerForm(FlaskForm):
    """Base customer form"""
    name = StringField(
        'Name', 
        validators=[DataRequired(message="Name is required")]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address")
        ]
    )
    
    company = StringField(
        'Company',
        validators=[DataRequired(message="Company is required")]
    )
    
    phone = StringField(
        'Phone',
        validators=[Optional()]
    )
    
    position = StringField(
        'Position',
        validators=[Optional()]
    )

class FileUploadForm(FlaskForm):
    """Base file upload form"""
    file = FileField(
        'File',
        validators=[DataRequired(message="File is required")]
    )
    
    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )

class DateRangeForm(FlaskForm):
    """Base date range form"""
    start_date = DateTimeField(
        'Start Date',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    
    end_date = DateTimeField(
        'End Date',
        validators=[Optional()],
        format='%Y-%m-%d'
    )

class PriceForm(FlaskForm):
    """Base price form"""
    list_price = DecimalField(
        'List Price',
        validators=[
            DataRequired(message="List price is required"),
        ]
    )
    
    sell_price = DecimalField(
        'Sell Price',
        validators=[
            DataRequired(message="Sell price is required"),
        ]
    )
    
    def validate_sell_price(self, field):
        """Validate sell price is not greater than list price"""
        if self.list_price.data and field.data > self.list_price.data:
            raise ValidationError("Sell price cannot be greater than list price")

class FilterForm(FlaskForm):
    """Base filter form"""
    min_value = DecimalField(
        'Minimum Value',
        validators=[Optional()]
    )
    
    max_value = DecimalField(
        'Maximum Value',
        validators=[Optional()]
    )
    
    def validate(self):
        """Validate min value is not greater than max value"""
        if not super().validate():
            return False
            
        if self.min_value.data and self.max_value.data:
            if self.min_value.data > self.max_value.data:
                self.min_value.errors.append("Minimum value cannot be greater than maximum value")
                return False
                
        return True

# Form mixins
class TimestampMixin:
    """Mixin for forms that need timestamp fields"""
    created_at = DateTimeField(
        'Created At',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M:%S'
    )
    
    updated_at = DateTimeField(
        'Updated At',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M:%S'
    )

class DescriptionMixin:
    """Mixin for forms that need description fields"""
    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )
    
    notes = TextAreaField(
        'Notes',
        validators=[Optional()]
    )