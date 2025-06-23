from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    SelectField, 
    TextAreaField,
    IntegerField,
    SubmitField,
    DecimalField,
    DateField
)
from wtforms.validators import DataRequired, Optional
from .validators import unique_deal_name  # Import our new validator

from app.models import DealType, AustralianState, DealStage, User, Contact, Company

class DealForm(FlaskForm):
    """Form for creating a new deal with the redesigned workflow."""
    
    project_name = StringField(
        'Deal Name', 
        validators=[
            DataRequired(message="Deal name is required."),
            unique_deal_name  # Use the custom validator
        ]
    )
    
    deal_type = SelectField(
        'Category',  # Relabeled from "Deal Type"
        choices=[(t.name, t.value) for t in DealType],
        validators=[DataRequired(message="Category is required.")]
    )
    
    state = SelectField(
        'State',
        choices=[(s.name, s.value) for s in AustralianState],
        validators=[DataRequired(message="State is required.")]
    )

    # These fields will be populated by the new search UI, not directly by the user.
    contact_id = IntegerField('Contact ID', validators=[Optional()])
    company_id = IntegerField('Company ID', validators=[Optional()])

    submit = SubmitField('Create Deal')


# The other forms below remain unchanged for now.
class QuoteForm(FlaskForm):
    deal_id = IntegerField('Deal ID', validators=[DataRequired(message="Deal ID is required")])
    revision_notes = TextAreaField('Revision Notes', validators=[Optional()])

class QuoteLineItemForm(FlaskForm):
    pump_assembly_id = IntegerField('Pump Assembly ID', validators=[DataRequired(message="Pump assembly is required")])
    quantity = IntegerField('Quantity', validators=[DataRequired(message="Quantity is required")], default=1)
    description = TextAreaField('Description', validators=[Optional()])
    sell_price = DecimalField('Sell Price', validators=[DataRequired(message="Sell price is required")])
    cost_price = DecimalField('Cost Price', validators=[DataRequired(message="Cost price is required")])

class DealCustomerForm(FlaskForm):
    customer_id = IntegerField('Customer ID', validators=[DataRequired(message="Customer ID is required")])

class DealStageUpdateForm(FlaskForm):
    stage = SelectField('Stage', choices=[(stage.name, stage.value) for stage in DealStage], validators=[DataRequired(message="Stage is required")])

class QuoteRevisionForm(FlaskForm):
    notes = TextAreaField('Revision Notes', validators=[DataRequired(message="Revision notes are required")])