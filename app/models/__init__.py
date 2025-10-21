from .base_model import BaseModel
from .customers.company_model import Company
from .customers.customer_model import Contact
from .deals.deal_models import Deal, QuoteRecipient, Quote, QuoteOption, QuoteLineItem, Discount
from .deals.quote_snapshot import QuoteSnapshot
from .deals.deal_types import DealStage, DealType, AustralianState
from .user_model import User, UserRole

# --- NEW: Import the Product model ---
from .products.product_model import Product

# --- Import Pump models ---
# TODO: Uncomment when pump models are implemented
# from .pumps import (
#     PumpSeries, Pump, PumpComponent, PumpBOM,
#     InertiaBase, SeismicSpring, RubberMount, Crossbar,
#     MotorProtection, DripTripTray,
#     PumpDutyPoint, PumpSelectionHistory, PumpConfidenceScore
# )



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
    
    # --- Export Pump models ---
    # TODO: Uncomment when pump models are implemented
    # 'PumpSeries',
    # 'Pump',
    # 'PumpComponent',
    # 'PumpBOM',
    # 'InertiaBase',
    # 'SeismicSpring',
    # 'RubberMount',
    # 'Crossbar',
    # 'MotorProtection',
    # 'DripTripTray',
    # 'PumpDutyPoint',
    # 'PumpSelectionHistory',
    # 'PumpConfidenceScore',
    
    # --- Export CRM models ---
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