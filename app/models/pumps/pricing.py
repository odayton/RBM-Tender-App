from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, Boolean, Text
from sqlalchemy.orm import relationship, validates
from ..base_model import BaseModel
from app.core.core_errors import ValidationError

class ComponentPrice(BaseModel):
    """Base model for component pricing history"""
    __tablename__ = 'component_prices'
    
    # Price identification
    component_type = Column(String(50), nullable=False)  # 'pump', 'inertia_base', 'spring', etc.
    component_id = Column(Integer, nullable=False)
    reference_number = Column(String(100))  # Part number or reference
    
    # Price information
    list_price = Column(Numeric(10, 2), nullable=False)
    net_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='EUR')
    
    # Validity period
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime)
    
    # Additional info
    notes = Column(Text)
    is_active = Column(Boolean, default=True)

    @validates('net_price')
    def validate_net_price(self, key, net_price):
        """Validate net price is not higher than list price"""
        if hasattr(self, 'list_price') and self.list_price is not None:
            if Decimal(str(net_price)) > Decimal(str(self.list_price)):
                raise ValidationError("Net price cannot be higher than list price")
        return net_price

    def calculate_margin(self) -> float:
        """Calculate margin percentage"""
        if not self.list_price or not self.net_price:
            return 0.0
        margin = ((Decimal(str(self.list_price)) - Decimal(str(self.net_price))) 
                 / Decimal(str(self.list_price)) * 100)
        return float(margin)

class PriceList(BaseModel):
    """Model for managing price lists"""
    __tablename__ = 'price_lists'
    
    name = Column(String(100), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime)
    currency = Column(String(3), default='EUR')
    is_active = Column(Boolean, default=True)
    
    # Relationships
    price_items = relationship("PriceListItem", back_populates="price_list", cascade="all, delete-orphan")

    def get_price(self, component_type: str, component_id: int) -> Optional[Dict[str, Any]]:
        """Get price for specific component"""
        price_item = next(
            (item for item in self.price_items 
             if item.component_type == component_type 
             and item.component_id == component_id),
            None
        )
        if price_item:
            return {
                'list_price': price_item.list_price,
                'net_price': price_item.net_price,
                'currency': self.currency
            }
        return None

class PriceListItem(BaseModel):
    """Model for individual price list items"""
    __tablename__ = 'price_list_items'
    
    price_list_id = Column(Integer, ForeignKey('price_lists.id'), nullable=False)
    component_type = Column(String(50), nullable=False)
    component_id = Column(Integer, nullable=False)
    reference_number = Column(String(100))
    
    list_price = Column(Numeric(10, 2), nullable=False)
    net_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationship
    price_list = relationship("PriceList", back_populates="price_items")

    @validates('net_price')
    def validate_net_price(self, key, net_price):
        """Validate net price is not higher than list price"""
        if hasattr(self, 'list_price') and self.list_price is not None:
            if Decimal(str(net_price)) > Decimal(str(self.list_price)):
                raise ValidationError("Net price cannot be higher than list price")
        return net_price

class DiscountRule(BaseModel):
    """Model for managing discount rules"""
    __tablename__ = 'discount_rules'
    
    name = Column(String(100), nullable=False)
    component_type = Column(String(50))  # If None, applies to all components
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    min_quantity = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime)
    
    def apply_discount(self, list_price: Decimal, quantity: int = 1) -> Decimal:
        """
        Apply discount rule to price
        Args:
            list_price: Original list price
            quantity: Quantity of items
        Returns:
            Decimal: Discounted price
        """
        if not self.is_active or quantity < self.min_quantity:
            return list_price
            
        if self.valid_to and datetime.utcnow() > self.valid_to:
            return list_price
            
        discount = Decimal(str(self.discount_percentage)) / Decimal('100')
        return list_price * (Decimal('1') - discount)

    def to_dict(self) -> Dict[str, Any]:
        """Convert discount rule to dictionary"""
        data = super().to_dict()
        data['is_valid'] = (
            self.is_active and 
            (not self.valid_to or datetime.utcnow() <= self.valid_to)
        )
        return data