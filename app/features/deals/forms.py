from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    SelectField, 
    DecimalField, 
    TextAreaField,
    IntegerField,
    DateTimeField,
    SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField

# Correct the import paths for the models
from app.models.deals.deal_types import DealType, AustralianState, DealStage
from app.models.user_model import User
from app.models.customers.customer_model import Contact # Changed from Customer
from app.models.customers.company_model import Company


# Query factories are updated to use the correct model
def get_deal_owners():
    return User.query

def get_contacts():
    return Contact.query # Changed from Customer

def get_companies():
    return Company.query


class DealForm(FlaskForm):
    """Form for creating and editing deals."""
    
    project_name = StringField(
        'Project Name', 
        validators=[DataRequired(message="Project name is required")]
    )
    
    state = SelectField(
        'State',
        choices=[(state.name, state.value) for state in AustralianState],
        validators=[DataRequired(message="State is required")]
    )
    
    deal_type = SelectField(
        'Deal Type',
        choices=[(type.name, type.value) for type in DealType],
        validators=[DataRequired(message="Deal type is required")]
    )
    
    stage = SelectField(
        'Stage',
        choices=[(stage.name, stage.value) for stage in DealStage],
        validators=[DataRequired(message="Stage is required")]
    )
    
    total_amount = DecimalField(
        'Total Amount',
        validators=[
            DataRequired(message="Total amount is required"),
            NumberRange(min=0, message="Total amount must be positive")
        ]
    )
    
    created_date = DateTimeField(
        'Created Date',
        validators=[DataRequired(message="Created date is required")],
        format='%Y-%m-%d'
    )
    
    deal_owner_id = IntegerField(
        'Deal Owner ID',
        validators=[Optional()]
    )

    contact_id = IntegerField(
        'Contact ID',
        validators=[Optional()]
    )

    company_id = IntegerField(
        'Company ID',
        validators=[Optional()]
    )

    submit = SubmitField('Save Changes')


class QuoteForm(FlaskForm):
    """Form for creating and editing quotes"""
    
    deal_id = IntegerField(
        'Deal ID',
        validators=[DataRequired(message="Deal ID is required")]
    )
    
    revision_notes = TextAreaField(
        'Revision Notes',
        validators=[Optional()]
    )

class QuoteLineItemForm(FlaskForm):
    """Form for quote line items"""
    
    pump_assembly_id = IntegerField(
        'Pump Assembly ID',
        validators=[DataRequired(message="Pump assembly is required")]
    )
    
    quantity = IntegerField(
        'Quantity',
        validators=[
            DataRequired(message="Quantity is required"),
            NumberRange(min=1, message="Quantity must be at least 1")
        ],
        default=1
    )
    
    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )
    
    sell_price = DecimalField(
        'Sell Price',
        validators=[
            DataRequired(message="Sell price is required"),
            NumberRange(min=0, message="Sell price must be positive")
        ]
    )
    
    cost_price = DecimalField(
        'Cost Price',
        validators=[
            DataRequired(message="Cost price is required"),
            NumberRange(min=0, message="Sell price must be positive")
        ]
    )

class DealCustomerForm(FlaskForm):
    """Form for adding customers to a deal"""
    
    customer_id = IntegerField(
        'Customer ID',
        validators=[DataRequired(message="Customer ID is required")]
    )

class DealStageUpdateForm(FlaskForm):
    """Form for updating deal stage"""
    
    stage = SelectField(
        'Stage',
        choices=[(stage.name, stage.value) for stage in DealStage],
        validators=[DataRequired(message="Stage is required")]
    )

class QuoteRevisionForm(FlaskForm):
    """Form for creating new quote revisions"""
    
    notes = TextAreaField(
        'Revision Notes',
        validators=[DataRequired(message="Revision notes are required")]
    )