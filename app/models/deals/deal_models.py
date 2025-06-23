from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from ..base_model import BaseModel
from .deal_associations import deal_contacts, deal_companies

class Deal(BaseModel):
    __tablename__ = 'deals'
    project_name = Column(String(200), nullable=False, unique=True)
    # ... other deal columns remain the same

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="deals")
    
    # NEW: A Deal has many streams/recipients
    recipients = relationship("QuoteRecipient", back_populates="deal", cascade="all, delete-orphan")
    
    contacts = relationship("Contact", secondary=deal_contacts, back_populates="deals")
    companies = relationship("Company", secondary=deal_companies, back_populates="deals")

class QuoteRecipient(BaseModel):
    """
    Represents a 'quote stream' for a specific company on a specific deal.
    This is the link that allows each company to have its own revision history.
    """
    __tablename__ = 'quote_recipients'
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)

    deal = relationship("Deal", back_populates="recipients")
    company = relationship("Company", back_populates="quote_streams")
    quotes = relationship("Quote", back_populates="recipient", cascade="all, delete-orphan")

class Quote(BaseModel):
    """Model for a single quote revision within a recipient's stream."""
    __tablename__ = 'quotes'
    recipient_id = Column(Integer, ForeignKey('quote_recipients.id'), nullable=False)
    revision = Column(Integer, nullable=False, default=1)
    notes = Text()

    recipient = relationship("QuoteRecipient", back_populates="quotes")
    # NEW: A Quote has many Options
    options = relationship("QuoteOption", back_populates="quote", cascade="all, delete-orphan")

class QuoteOption(BaseModel):
    """Represents a specific pricing option within a single quote revision."""
    __tablename__ = 'quote_options'
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    name = Column(String(120), nullable=False, default="Main Option") # e.g., "Pumps Only"

    quote = relationship("Quote", back_populates="options")
    line_items = relationship("QuoteLineItem", back_populates="option", cascade="all, delete-orphan")

class QuoteLineItem(BaseModel):
    """Model for individual line items, now belonging to a QuoteOption."""
    __tablename__ = 'quote_line_items'
    option_id = Column(Integer, ForeignKey('quote_options.id'), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)

    option = relationship("QuoteOption", back_populates="line_items")