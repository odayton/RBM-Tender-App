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

from app.models import DealType, AustralianState, DealStage, User

class UpdateDealForm(FlaskForm):
    """Form for editing an existing deal's core details."""
    id = HiddenField("Deal ID")
    project_name = StringField(
        'Project Name',
        validators=[DataRequired(), unique_deal_name]
    )
    deal_type = SelectField(
        'Category',
        choices=[(t.name, t.value) for t in DealType],
        validators=[DataRequired()]
    )
    stage = SelectField(
        'Stage',
        choices=[(s.name, s.value) for s in DealStage],
        validators=[DataRequired()]
    )
    state = SelectField(
        'State',
        choices=[(s.name, s.value) for s in AustralianState],
        validators=[DataRequired()]
    )
    owner_id = SelectField('Deal Owner', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        super(UpdateDealForm, self).__init__(*args, **kwargs)
        # Populate owner choices dynamically
        self.owner_id.choices = [(u.id, u.username) for u in User.query.order_by('username').all()]


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
    deal_type = SelectField('Category', choices=[(t.name, t.value) for t in DealType])
    state = SelectField('State', choices=[(s.name, s.value) for s in AustralianState])
    contact_id = IntegerField('Contact ID', validators=[Optional()])
    company_id = IntegerField('Company ID', validators=[Optional()])
    submit = SubmitField('Create Deal')