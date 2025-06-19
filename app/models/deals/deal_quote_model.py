from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from ..base_model import BaseModel
from app.core.core_errors import ValidationError
# Import the association table from its new, dedicated file
from .deal_associations import deal_customers


class QuoteLineItem(BaseModel):
    """Model for individual line items within a quote"""
    __tablename__ = 'quote_line_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    quote = relationship("Quote", back_populates="line_items")
    
    def __init__(self, quote_id: int, description: str, quantity: int, unit_price: Decimal):
        self.quote_id = quote_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = quantity * unit_price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "quote_id": self.quote_id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
            "total_price": str(self.total_price)
        }

class Quote(BaseModel):
    """Model for managing quotes"""
    __tablename__ = 'quotes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    quote_number = Column(String(50), nullable=False, unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=False)
    
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    deal = relationship("Deal", back_populates="quotes")
    line_items = relationship("QuoteLineItem", back_populates="quote", cascade="all, delete-orphan")
    customer = relationship("Customer", back_populates="quotes")
    
    def __init__(self, deal_id: int, customer_id: int, quote_number: str, amount: Decimal, valid_until: datetime):
        self.deal_id = deal_id
        self.customer_id = customer_id
        self.quote_number = quote_number
        self.amount = amount
        self.valid_until = valid_until
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "deal_id": self.deal_id,
            "customer_id": self.customer_id,
            "quote_number": self.quote_number,
            "amount": str(self.amount),
            "created_date": self.created_date.isoformat(),
            "valid_until": self.valid_until.isoformat()
        }
    
    @staticmethod
    def validate_quote_number(quote_number: str) -> None:
        if not quote_number:
            raise ValidationError("Quote number cannot be empty.")
        if len(quote_number) > 50:
            raise ValidationError("Quote number cannot exceed 50 characters.")


class AustralianState(enum.Enum):
    """Australian states and territories"""
    NSW = "New South Wales"
    VIC = "Victoria"
    QLD = "Queensland"
    WA = "Western Australia"
    SA = "South Australia"
    TAS = "Tasmania"
    NT = "Northern Territory"
    ACT = "Australian Capital Territory"

class DealType(enum.Enum):
    """Types of deals"""
    HVAC = "HVAC"
    HYDRAULIC = "Hydraulic"
    HYDRONIC = "Hydronic"
    DATA_CENTRES = "Data Centres"
    MERCHANT = "Merchant"
    WHOLESALER = "Wholesaler"
    OEM = "OEM"

class DealStage(enum.Enum):
    """Deal pipeline stages"""
    SALES_LEAD = "Sales Lead"
    TENDER = "Tender"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    ABANDONED = "Abandoned"

class Deal(BaseModel):
    """Model for managing deals"""
    __tablename__ = 'deals'
    
    project_name = Column(String(200), nullable=False)
    state = Column(Enum(AustralianState), nullable=False)
    deal_type = Column(Enum(DealType), nullable=False)
    stage = Column(Enum(DealStage), nullable=False, default=DealStage.SALES_LEAD)
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    company = relationship("Company", back_populates="deals")
    owner = relationship("User", back_populates="deals")
    customers = relationship("Customer", secondary=deal_customers, back_populates="deals")
    quotes = relationship("Quote", back_populates="deal", cascade="all, delete-orphan")