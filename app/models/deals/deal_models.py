from typing import Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from ..base_model import BaseModel
from ...core.core_errors import ValidationError
# Import from our new, separated files
from .deal_associations import deal_contacts
from .deal_types import AustralianState, DealType, DealStage


class Deal(BaseModel):
    """Model for managing deals/projects."""
    __tablename__ = 'deals'
    
    # --- Columns ---
    project_name = Column(String(200), nullable=False)
    state = Column(SQLAlchemyEnum(AustralianState), nullable=False)
    deal_type = Column(SQLAlchemyEnum(DealType), nullable=False)
    stage = Column(SQLAlchemyEnum(DealStage), nullable=False, default=DealStage.SALES_LEAD)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # --- Foreign Keys ---
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id')) # A deal can be unassigned
    
    # --- Relationships ---
    company = relationship("Company", back_populates="deals")
    owner = relationship("User", back_populates="deals")
    contacts = relationship("Contact", secondary=deal_contacts, back_populates="deals")
    quotes = relationship("Quote", back_populates="deal", cascade="all, delete-orphan")


class Quote(BaseModel):
    """Model for managing quotes, which belong to a deal."""
    __tablename__ = 'quotes'
    
    # --- Columns ---
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    quote_number = Column(String(50), nullable=False, unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    
    # --- Relationships ---
    deal = relationship("Deal", back_populates="quotes")
    contact = relationship("Contact", back_populates="quotes")
    line_items = relationship("QuoteLineItem", back_populates="quote", cascade="all, delete-orphan")

    def validate(self) -> None:
        """Custom validation for quote data."""
        super().validate()
        if not self.quote_number:
            raise ValidationError("Quote number cannot be empty.")
        if len(self.quote_number) > 50:
            raise ValidationError("Quote number cannot exceed 50 characters.")


class QuoteLineItem(BaseModel):
    """Model for individual line items within a quote."""
    __tablename__ = 'quote_line_items'
    
    # --- Columns ---
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    # --- Relationships ---
    quote = relationship("Quote", back_populates="line_items")

    @property
    def total_price(self) -> Decimal:
        """Calculated property for the total price."""
        return (self.quantity or 0) * (self.unit_price or 0)