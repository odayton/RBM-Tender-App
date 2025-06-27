from wtforms.validators import ValidationError
from decimal import Decimal
from datetime import datetime
from app.models import Deal, Quote, DealStage
from app.core.core_errors import ValidationError as AppValidationError

# This is the new WTForms-compatible validator
def unique_deal_name(form, field):
    """
    Checks if a deal name (project_name) is unique, allowing for edits.
    """
    try:
        # Check for an existing deal_id on the form
        deal_id = form.id.data if hasattr(form, 'id') else None
        validate_project_name_unique(field.data, deal_id=deal_id)
    except AppValidationError as e:
        raise ValidationError(str(e))

def validate_project_name_unique(project_name: str, deal_id: int = None) -> bool:
    """Helper function to check for project name uniqueness in the database."""
    query = Deal.query.filter(Deal.project_name.ilike(project_name))
    if deal_id:
        # If we are editing a deal, exclude it from the uniqueness check
        query = query.filter(Deal.id != deal_id)
    if query.first():
        raise AppValidationError(f"A deal with the name '{project_name}' already exists.")
    return True

def validate_deal_stage_transition(old_stage: DealStage, new_stage: DealStage) -> bool:
    allowed_transitions = {
        DealStage.SALES_LEAD: [DealStage.TENDER, DealStage.ABANDONED],
        DealStage.TENDER: [DealStage.PROPOSAL, DealStage.LOST, DealStage.ABANDONED],
        DealStage.PROPOSAL: [DealStage.NEGOTIATION, DealStage.LOST, DealStage.ABANDONED],
        DealStage.NEGOTIATION: [DealStage.WON, DealStage.LOST, DealStage.ABANDONED],
        DealStage.WON: [],
        DealStage.LOST: [DealStage.SALES_LEAD],
        DealStage.ABANDONED: [DealStage.SALES_LEAD]
    }
    if new_stage not in allowed_transitions.get(old_stage, []):
        raise AppValidationError(f"Cannot transition from {old_stage.value} to {new_stage.value}")
    return True

def validate_total_amount(form, field):
    if field.data <= 0:
        raise ValidationError("Total amount must be greater than 0")

def validate_quote_revision(quote: Quote) -> bool:
    if quote.deal.stage in [DealStage.WON, DealStage.LOST, DealStage.ABANDONED]:
        raise AppValidationError("Cannot revise quote in current deal stage")
    return True

def validate_line_item(quantity: Decimal, sell_price: Decimal) -> bool:
    if quantity <= 0:
        raise AppValidationError("Quantity must be greater than 0")
    if sell_price <= 0:
        raise AppValidationError("Sell price must be greater than 0")
    return True

def validate_project_name_unique(project_name: str, deal_id: int = None) -> bool:
    query = Deal.query.filter(Deal.project_name.ilike(project_name))
    if deal_id:
        query = query.filter(Deal.id != deal_id)
    if query.first():
        raise AppValidationError(f"A deal with the name '{project_name}' already exists.")
    return True

def validate_created_date(date: datetime) -> bool:
    if date > datetime.now():
        raise AppValidationError("Created date cannot be in the future")
    return True

def validate_deal_editable(deal: Deal) -> bool:
    if deal.stage in [DealStage.WON, DealStage.LOST]:
        raise AppValidationError("Cannot edit deal in current stage")
    return True

def validate_quote_deletable(quote: Quote) -> bool:
    if quote.deal.stage in [DealStage.WON, DealStage.LOST, DealStage.ABANDONED]:
        raise AppValidationError("Cannot delete quote in current deal stage")
    if len(quote.deal.quotes) <= 1:
        raise AppValidationError("Cannot delete the only quote in a deal")
    return True