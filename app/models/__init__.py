from .base_model import BaseModel
from .customers.company_model import Company
from .customers.customer_model import Contact
from .deals.deal_models import Deal, QuoteRecipient, Quote, QuoteOption, QuoteLineItem
from .deals.deal_types import DealStage, DealType, AustralianState
from .user_model import User, UserRole

# --- NEW: Import the Product model ---
from .products.product_model import Product

from .pumps.pump_model import (
    Pump,
    InertiaBase,
    SeismicSpring,
    RubberMount,
)
from .pumps.pump_assembly import PumpAssembly
from .pumps.pricing import PriceList, PriceListItem, DiscountRule, AdditionalPriceAdder


__all__ = [
    'BaseModel',
    'Company',
    'Contact',
    'Deal',
    'QuoteRecipient',
    'Quote',
    'QuoteOption',
    'QuoteLineItem',
    'DealStage',
    'DealType',
    'AustralianState',
    'User',
    'UserRole',
    'Pump',
    'InertiaBase',
    'SeismicSpring',
    'RubberMount',
    'PumpAssembly',
    'PriceList',
    'PriceListItem',
    'DiscountRule',
    'AdditionalPriceAdder',
    # --- NEW: Export the Product model ---
    'Product'
]