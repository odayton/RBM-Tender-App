from wtforms.validators import ValidationError
from decimal import Decimal
from datetime import datetime
from app.models.deals.deal_quote_model import Deal, Quote, DealStage
from app.core.core_errors import ValidationError as AppValidationError

def validate_deal_stage_transition(old_stage: DealStage, new_stage: DealStage) -> bool:
    """
    Validate if a deal stage transition is allowed
    
    Args:
        old_stage: Current stage of the deal
        new_stage: Proposed new stage
    Returns:
        bool: True if transition is valid
    Raises:
        ValidationError: If transition is not allowed
    """
    allowed_transitions = {
        DealStage.SALES_LEAD: [DealStage.TENDER, DealStage.ABANDONED],
        DealStage.TENDER: [DealStage.PROPOSAL, DealStage.LOST, DealStage.ABANDONED],
        DealStage.PROPOSAL: [DealStage.NEGOTIATION, DealStage.LOST, DealStage.ABANDONED],
        DealStage.NEGOTIATION: [DealStage.WON, DealStage.LOST, DealStage.ABANDONED],
        DealStage.WON: [],  # No transitions from Won
        DealStage.LOST: [DealStage.SALES_LEAD],  # Can reopen as Sales Lead
        DealStage.ABANDONED: [DealStage.SALES_LEAD]  # Can reopen as Sales Lead
    }
    
    if new_stage not in allowed_transitions.get(old_stage, []):
        raise ValidationError(
            f"Cannot transition from {old_stage.value} to {new_stage.value}"
        )
    
    return True

def validate_total_amount(form, field):
    """
    Validate deal total amount
    Raises:
        ValidationError: If amount is invalid
    """
    if field.data <= 0:
        raise ValidationError("Total amount must be greater than 0")

def validate_quote_revision(quote: Quote) -> bool:
    """
    Validate if a quote can be revised
    
    Args:
        quote: Quote to validate
    Returns:
        bool: True if revision is allowed
    Raises:
        ValidationError: If revision is not allowed
    """
    if quote.deal.stage in [DealStage.WON, DealStage.LOST, DealStage.ABANDONED]:
        raise AppValidationError(
            "Cannot revise quote in current deal stage"
        )
    return True

def validate_line_item(quantity: Decimal, sell_price: Decimal) -> bool:
    """
    Validate quote line item
    
    Args:
        quantity: Item quantity
        sell_price: Selling price
    Returns:
        bool: True if valid
    Raises:
        ValidationError: If validation fails
    """
    if quantity <= 0:
        raise AppValidationError("Quantity must be greater than 0")
        
    if sell_price <= 0:
        raise AppValidationError("Sell price must be greater than 0")
    
    return True

def validate_project_name_unique(project_name: str, deal_id: int = None) -> bool:
    """
    Validate project name is unique
    
    Args:
        project_name: Name to validate
        deal_id: Optional deal ID to exclude from check
    Returns:
        bool: True if valid
    Raises:
        ValidationError: If name is not unique
    """
    query = Deal.query.filter(Deal.project_name == project_name)
    if deal_id:
        query = query.filter(Deal.id != deal_id)
    
    if query.first():
        raise AppValidationError(
            f"Project name '{project_name}' already exists"
        )
    return True

def validate_created_date(date: datetime) -> bool:
    """
    Validate deal created date
    
    Args:
        date: Date to validate
    Returns:
        bool: True if valid
    Raises:
        ValidationError: If date is invalid
    """
    if date > datetime.now():
        raise AppValidationError("Created date cannot be in the future")
    return True

def validate_deal_editable(deal: Deal) -> bool:
    """
    Validate if a deal can be edited
    
    Args:
        deal: Deal to validate
    Returns:
        bool: True if editable
    Raises:
        ValidationError: If deal cannot be edited
    """
    if deal.stage in [DealStage.WON, DealStage.LOST]:
        raise AppValidationError(
            "Cannot edit deal in current stage"
        )
    return True

def validate_quote_deletable(quote: Quote) -> bool:
    """
    Validate if a quote can be deleted
    
    Args:
        quote: Quote to validate
    Returns:
        bool: True if deletable
    Raises:
        ValidationError: If quote cannot be deleted
    """
    if quote.deal.stage in [DealStage.WON, DealStage.LOST, DealStage.ABANDONED]:
        raise AppValidationError(
            "Cannot delete quote in current deal stage"
        )
        
    if len(quote.deal.quotes) <= 1:
        raise AppValidationError(
            "Cannot delete the only quote in a deal"
        )
    
    return True