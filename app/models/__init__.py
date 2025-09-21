from .base_model import BaseModel
from .customers.company_model import Company
from .customers.customer_model import Contact
from .deals.deal_models import Deal, QuoteRecipient, Quote, QuoteOption, QuoteLineItem, Discount
from .deals.quote_snapshot import QuoteSnapshot
from .deals.deal_types import DealStage, DealType, AustralianState
from .user_model import User, UserRole

# --- NEW: Import the Product model ---
from .products.product_model import Product

# Pump models removed - no longer needed



# Import CRM models
from .crm import (
    Activity, ActivityType, ActivityStatus,
    Task, TaskPriority, TaskStatus, TaskType,
    Call, Email, Meeting, Note,
    CallDirection, CallOutcome, EmailDirection, MeetingType, NoteType
)


__all__ = [
    'BaseModel',
    'Company',
    'Contact',
    'Deal',
    'QuoteRecipient',
    'Quote',
    'QuoteOption',
    'QuoteLineItem',
    'Discount',
    'QuoteSnapshot',
    'DealStage',
    'DealType',
    'AustralianState',
    'User',
    'UserRole',

    # --- NEW: Export the Product model ---
    'Product',
    
    # Pump models removed - no longer needed
    # --- NEW: Export CRM models ---
    'Activity',
    'ActivityType',
    'ActivityStatus',
    'Task',
    'TaskPriority',
    'TaskStatus',
    'TaskType',
    'Call',
    'Email',
    'Meeting',
    'Note',
    'CallDirection',
    'CallOutcome',
    'EmailDirection',
    'MeetingType',
    'NoteType'
]