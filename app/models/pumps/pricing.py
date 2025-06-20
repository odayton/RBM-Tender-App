from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, Boolean, Text
from sqlalchemy.orm import relationship, validates

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class PriceList(BaseModel):
    """
    Represents a specific price list (e.g., "Standard 2024", "VIP Customer Pricing").
    Inherits id, created_at, and updated_at from BaseModel.
    """
    __tablename__ = 'price_lists'
    
    name = Column(String(100), nullable=False, unique=True)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime)
    currency = Column(String(3), default='AUD', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # A price list contains many individual price items.
    price_items = relationship("PriceListItem", back_populates="price_list", cascade="all, delete-orphan")

class PriceListItem(BaseModel):
    """
    Represents a single item within a PriceList.
    This uses a polymorphic association to link to any component type.
    """
    __tablename__ = 'price_list_items'
    
    price_list_id = Column(Integer, ForeignKey('price_lists.id'), nullable=False)
    
    # Polymorphic association fields
    component_type = Column(String(50), nullable=False, index=True) # e.g., 'pump', 'inertia_base'
    component_part_number = Column(String(100), nullable=False, index=True) # The part_number or SKU
    
    list_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationship back to the parent PriceList
    price_list = relationship("PriceList", back_populates="price_items")

    def validate(self):
        super().validate()
        if self.list_price < 0:
            raise ValidationError("List price cannot be negative.")

class DiscountRule(BaseModel):
    """
    Model for managing discount rules that can be applied to components.
    """
    __tablename__ = 'discount_rules'
    
    name = Column(String(100), nullable=False)
    # If component_type is null, the rule applies to all components.
    component_type = Column(String(50), index=True) 
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    min_quantity = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_to = Column(DateTime)

    def is_currently_valid(self) -> bool:
        """Checks if the discount rule is active and within its date range."""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_to and self.valid_to < now:
            return False
        return True

    def apply_discount(self, list_price: Decimal, quantity: int = 1) -> Decimal:
        """Applies the discount to a given price if the rule is valid."""
        if not self.is_currently_valid() or quantity < self.min_quantity:
            return list_price
            
        discount_factor = Decimal(self.discount_percentage or 0) / Decimal('100')
        return list_price * (Decimal('1') - discount_factor)

# The ComponentPrice model for tracking price history is a good idea,
# but can be implemented later. For now, PriceList is the primary mechanism.
# We will comment it out to simplify the initial schema.

# class ComponentPrice(BaseModel):
#     """Base model for component pricing history"""
#     __tablename__ = 'component_prices'
#     ...