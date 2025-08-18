from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, Boolean, Text
from sqlalchemy.orm import relationship, validates

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class PriceList(BaseModel):
    __tablename__ = 'price_lists'
    
    name = Column(String(100), nullable=False, unique=True)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime)
    currency = Column(String(3), default='AUD', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    price_items = relationship("PriceListItem", back_populates="price_list", cascade="all, delete-orphan")

class PriceListItem(BaseModel):
    __tablename__ = 'price_list_items'
    
    price_list_id = Column(Integer, ForeignKey('price_lists.id'), nullable=False)
    
    component_type = Column(String(50), nullable=False, index=True)
    component_part_number = Column(String(100), nullable=False, index=True)
    
    list_price = Column(Numeric(10, 2), nullable=False)
    
    price_list = relationship("PriceList", back_populates="price_items")

    def validate(self):
        super().validate()
        if self.list_price < 0:
            raise ValidationError("List price cannot be negative.")

class DiscountRule(BaseModel):
    __tablename__ = 'discount_rules'
    
    name = Column(String(100), nullable=False)
    component_type = Column(String(50), index=True) 
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    min_quantity = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_to = Column(DateTime)

    def is_currently_valid(self) -> bool:
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_to and self.valid_to < now:
            return False
        return True

    def apply_discount(self, list_price: Decimal, quantity: int = 1) -> Decimal:
        if not self.is_currently_valid() or quantity < self.min_quantity:
            return list_price
            
        discount_factor = Decimal(self.discount_percentage or 0) / Decimal('100')
        return list_price * (Decimal('1') - discount_factor)

class AdditionalPriceAdder(BaseModel):
    __tablename__ = 'additional_price_adders'

    ip_adder = Column(Numeric(10, 2), nullable=False, default=0.0)
    drip_tray_adder = Column(Numeric(10, 2), nullable=False, default=0.0)
    # Adding name and description for completeness, can be nullable
    name = Column(String(100))
    description = Column(Text)

    def __repr__(self) -> str:
        return f"<AdditionalPriceAdder(id={self.id})>"