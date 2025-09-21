"""
Test factories for generating test data
"""

from .user_factory import UserFactory, AdminUserFactory, SalesUserFactory, ManagerUserFactory, ViewerUserFactory
from .company_factory import CompanyFactory
from .contact_factory import ContactFactory, PrimaryContactFactory
from .deal_factory import DealFactory, HVACDealFactory, PlumbingDealFactory, HydronicHeatingDealFactory, ClosedWonDealFactory, SalesLeadDealFactory
from .product_factory import ProductFactory, HVACProductFactory, PlumbingProductFactory, HydronicProductFactory, LowStockProductFactory, OutOfStockProductFactory
from .quote_factory import QuoteFactory, QuoteRecipientFactory, QuoteOptionFactory, QuoteLineItemFactory, MultiOptionQuoteFactory, SimpleQuoteFactory

__all__ = [
    'UserFactory',
    'AdminUserFactory',
    'SalesUserFactory', 
    'ManagerUserFactory',
    'ViewerUserFactory',
    'CompanyFactory', 
    'ContactFactory',
    'PrimaryContactFactory',
    'DealFactory',
    'HVACDealFactory',
    'PlumbingDealFactory',
    'HydronicHeatingDealFactory',
    'ClosedWonDealFactory',
    'SalesLeadDealFactory',
    'ProductFactory',
    'HVACProductFactory',
    'PlumbingProductFactory',
    'HydronicProductFactory',
    'LowStockProductFactory',
    'OutOfStockProductFactory',
    'QuoteFactory',
    'QuoteRecipientFactory',
    'QuoteOptionFactory',
    'QuoteLineItemFactory',
    'MultiOptionQuoteFactory',
    'SimpleQuoteFactory'
]
