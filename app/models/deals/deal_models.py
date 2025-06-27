from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from app.models.deals.deal_associations import deal_contacts, deal_companies
from app.models.deals.deal_types import DealStage, DealType, AustralianState
from app.models.products.product_model import Product

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
    recipient = relationship("QuoteRecipient", back_populates="quotes")
    options = relationship("QuoteOption", back_populates="quote", cascade="all, delete-orphan")

class QuoteOption(BaseModel):
    __tablename__ = 'quote_options'
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    name = Column(String(120), nullable=False, default="Main Option")
    freight_charge = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    quote = relationship("Quote", back_populates="options")
    # Order line items by the new display_order column
    line_items = relationship("QuoteLineItem", back_populates="option", cascade="all, delete-orphan", order_by="QuoteLineItem.display_order")

class QuoteLineItem(BaseModel):
    """Model for individual line items, now with discount and ordering."""
    __tablename__ = 'quote_line_items'
    
    option_id = Column(Integer, ForeignKey('quote_options.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)
    discount = Column(Numeric(5, 2), nullable=False, default=0.0) # Percentage
    display_order = Column(Integer, nullable=False, default=0)

    # Custom item fields (only used if product_id is NULL)
    custom_sku = Column(String(80))
    custom_name = Column(String(200))

    # Relationships
    option = relationship("QuoteOption", back_populates="line_items")
    product = relationship("Product")