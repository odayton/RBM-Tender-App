# app/models/deals/deal_models.py

from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from app.models.base_model import BaseModel
from app.models.deals.deal_associations import deal_contacts, deal_companies
from app.models.deals.deal_types import DealStage, DealType, AustralianState
from app.core.core_errors import ValidationError
from app.extensions import db

class Discount(BaseModel):
    __tablename__ = 'discounts'
    # --- CHANGE THIS LINE ---
    # The code should be unique, but not a primary key.
    code = Column(String(10), unique=True, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    products = relationship("Product", back_populates="discount")

class Deal(BaseModel):
    __tablename__ = 'deals'
    project_name = Column(String(200), nullable=False, unique=True)
    stage = Column(Enum(DealStage), nullable=False, default=DealStage.SALES_LEAD)
    deal_type = Column(Enum(DealType), nullable=False)
    state = Column(Enum(AustralianState), nullable=False)
    total_amount = Column(Numeric(10, 2), default=0.0)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="deals")
    recipients = relationship("QuoteRecipient", back_populates="deal", cascade="all, delete-orphan")
    contacts = relationship("Contact", secondary=deal_contacts, back_populates="deals")
    companies = relationship("Company", secondary=deal_companies, back_populates="deals")

    def validate(self) -> None:
        """Custom validation for deal data."""
        super().validate()
        
        if not self.project_name or len(self.project_name.strip()) < 3:
            raise ValidationError("Project name must be at least 3 characters long.")
        
        if not self.owner_id:
            raise ValidationError("Deal must have an owner assigned.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the deal instance to a dictionary."""
        data = super().to_dict()
        data['owner_name'] = self.owner.full_name if self.owner else None
        data['contact_count'] = len(self.contacts)
        data['company_count'] = len(self.companies)
        data['recipient_count'] = len(self.recipients)
        return data

    def get_total_quotes_value(self) -> Decimal:
        """Calculate total value of all quotes for this deal."""
        total = Decimal('0.0')
        for recipient in self.recipients:
            for quote in recipient.quotes:
                total += quote.total_price
        return total

    def get_latest_quote(self):
        """Get the most recent quote for this deal."""
        latest_quote = None
        latest_date = None
        
        for recipient in self.recipients:
            for quote in recipient.quotes:
                if not latest_date or quote.created_at > latest_date:
                    latest_date = quote.created_at
                    latest_quote = quote
        
        return latest_quote

    def can_be_edited_by(self, user) -> bool:
        """Check if a user can edit this deal."""
        if user.is_admin():
            return True
        if user.is_manager():
            return True
        if self.owner_id == user.id:
            return True
        return False

class QuoteRecipient(BaseModel):
    __tablename__ = 'quote_recipients'
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    deal = relationship("Deal", back_populates="recipients")
    company = relationship("Company", back_populates="quote_streams")
    quotes = relationship("Quote", back_populates="recipient", cascade="all, delete-orphan")

class Quote(BaseModel):
    __tablename__ = 'quotes'
    recipient_id = Column(Integer, ForeignKey('quote_recipients.id'), nullable=False)
    revision = Column(Integer, nullable=False, default=1)
    notes = Column(Text)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    
    recipient = relationship("QuoteRecipient", back_populates="quotes")
    options = relationship("QuoteOption", back_populates="quote", cascade="all, delete-orphan")

    @property
    def total_price(self):
        """Calculates the total price of the quote by summing its options."""
        return sum(option.total_price for option in self.options)

    @property
    def gst(self):
        """Calculates the GST amount for the quote."""
        return self.total_price * Decimal('0.10')

    @property
    def grand_total(self):
        """Calculates the grand total including GST."""
        return self.total_price + self.gst

class QuoteOption(BaseModel):
    __tablename__ = 'quote_options'
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    name = Column(String(120), nullable=False, default="Main Option")
    freight_charge = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    quote = relationship("Quote", back_populates="options")
    line_items = relationship("QuoteLineItem", back_populates="option", cascade="all, delete-orphan", order_by="QuoteLineItem.display_order")

    @property
    def total_price(self):
        """Calculates the total price of the option including freight."""
        line_item_total = sum(item.total_price for item in self.line_items)
        freight = self.freight_charge or 0
        return line_item_total + freight
        
    # --- NEW PROPERTIES ADDED TO OPTION ---
    @property
    def gst(self):
        """Calculates the GST amount for the option."""
        return self.total_price * Decimal('0.10')

    @property
    def grand_total(self):
        """Calculates the grand total for the option including GST."""
        return self.total_price + self.gst
    
    @property
    def subtotal(self):
        """Calculates the subtotal excluding freight."""
        line_item_total = sum(item.total_price for item in self.line_items)
        return line_item_total
    


class QuoteLineItem(BaseModel):
    """Model for individual line items, now with discount and ordering."""
    __tablename__ = 'quote_line_items'
    
    option_id = Column(Integer, ForeignKey('quote_options.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)
    discount = Column(Numeric(5, 2), nullable=False, default=0.0)
    display_order = Column(Integer, nullable=False, default=0)

    custom_sku = Column(String(80))
    custom_name = Column(String(200))

    option = relationship("QuoteOption", back_populates="line_items")
    product = relationship("Product")

    @property
    def total_price(self):
        """Calculates the final price for the line item, including discounts."""
        price = self.unit_price or Decimal('0.0')
        qty = self.quantity or 0
        disc = self.discount or Decimal('0.0')
        
        discount_amount = (price * (disc / Decimal('100')))
        final_unit_price = price - discount_amount
        return final_unit_price * Decimal(qty)