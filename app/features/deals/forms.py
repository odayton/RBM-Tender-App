from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    TextAreaField,
    IntegerField,
    SubmitField,
    DecimalField,
    HiddenField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from .validators import unique_deal_name

from app.models import DealType, AustralianState, DealStage, User, UserRole

class UpdateDealForm(FlaskForm):
    """Form for editing an existing deal's core details."""
    id = HiddenField("Deal ID")
    project_name = StringField(
        'Project Name',
        validators=[DataRequired(), unique_deal_name]
    )
    deal_type = SelectField(
        'Category',
        validators=[DataRequired()]
    )
    stage = SelectField(
        'Stage',
        validators=[DataRequired()]
    )
    state = SelectField(
        'State',
        validators=[DataRequired()]
    )
    owner_id = SelectField('Deal Owner', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        super(UpdateDealForm, self).__init__(*args, **kwargs)
        
        try:
            from flask import current_app
            if not current_app:
                return  # Skip population if no app context
            
            # Set choices for enum fields
            self.deal_type.choices = [(t.name, t.value) for t in DealType]
            self.stage.choices = [(s.name, s.value) for s in DealStage]
            self.state.choices = [(s.name, s.value) for s in AustralianState]
            
            # Populate owner choices dynamically - exclude admin users
            non_admin_users = User.query.filter(User.role != UserRole.ADMIN).order_by(User.username).all()
            self.owner_id.choices = [(u.id, u.full_name) for u in non_admin_users]
        except RuntimeError:
            # Skip population if we're outside application context
            pass


class QuoteOptionForm(FlaskForm):
    """Form for creating and editing a quote option's name."""
    name = StringField('Option Name', validators=[
        DataRequired(),
        Length(min=3, max=120)
    ])
    submit = SubmitField('Save Option')


class LineItemForm(FlaskForm):
    """Form for creating and editing a quote line item."""
    product_id = HiddenField("Product ID", validators=[Optional()])
    notes = TextAreaField('Custom Description', validators=[Optional(), Length(max=500)], render_kw={"rows": 3})
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired(), NumberRange(min=1)])
    unit_price = DecimalField('Unit Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    discount = DecimalField('Discount (%)', places=2, default=0.0, validators=[Optional(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save Item')


class DealForm(FlaskForm):
    """Form for creating a new deal."""
    project_name = StringField(
        'Deal Name',
        validators=[DataRequired(), unique_deal_name]
    )
    deal_type = SelectField('Category')
    state = SelectField('State')
    contact_id = IntegerField('Contact ID', validators=[Optional()])
    company_id = IntegerField('Company ID', validators=[Optional()])
    submit = SubmitField('Create Deal')
    
    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)
        
        try:
            from flask import current_app
            if not current_app:
                return  # Skip population if no app context
            
            # Set choices for enum fields
            self.deal_type.choices = [(t.name, t.value) for t in DealType]
            self.state.choices = [(s.name, s.value) for s in AustralianState]
        except RuntimeError:
            # Skip population if we're outside application context
            pass