# app/models/deals/deal_models.py

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, Enum, Boolean, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from app.models.base_model import BaseModel
from app.models.deals.deal_associations import deal_contacts, deal_companies
from app.models.deals.deal_types import DealStage, DealType, AustralianState
from app.core.core_errors import ValidationError
from app.extensions import db

class Discount(BaseModel):
    """Model for managing discount codes and their application to products."""
    __tablename__ = 'discounts'
    
    code = Column(String(10), unique=True, nullable=False, index=True)
    percentage = Column(Numeric(5, 2), nullable=False)
    description = Column(String(200))
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(db.DateTime)
    valid_until = Column(db.DateTime)
    
    # Relationships
    products = relationship("Product", back_populates="discount")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('percentage >= 0 AND percentage <= 100', name='check_discount_percentage'),
        Index('idx_discount_active', 'is_active'),
    )
    
    def validate(self) -> None:
        """Custom validation for discount data."""
        super().validate()
        
        if not self.code or len(self.code.strip()) < 2:
            raise ValidationError("Discount code must be at least 2 characters long.")
        
        if self.percentage < 0 or self.percentage > 100:
            raise ValidationError("Discount percentage must be between 0 and 100.")
        
        if self.valid_from and self.valid_until and self.valid_from >= self.valid_until:
            raise ValidationError("Valid from date must be before valid until date.")
    
    def is_valid(self) -> bool:
        """Check if discount is currently valid."""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return True

class Deal(BaseModel):
    """Model for managing sales deals and opportunities."""
    __tablename__ = 'deals'
    
    project_name = Column(String(200), nullable=False, unique=True, index=True)
    stage = Column(Enum(DealStage), nullable=False, default=DealStage.SALES_LEAD, index=True)
    deal_type = Column(Enum(DealType), nullable=False, index=True)
    state = Column(Enum(AustralianState), nullable=False)
    total_amount = Column(Numeric(10, 2), default=0.0)
    
    # Additional fields for better deal management
    description = Column(Text)
    expected_close_date = Column(db.DateTime)
    probability = Column(Numeric(5, 2), default=0.0)  # Percentage probability of closing
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text)
    
    # Foreign keys and relationships
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    owner = relationship("User", back_populates="deals")
    recipients = relationship("QuoteRecipient", back_populates="deal", cascade="all, delete-orphan")
    contacts = relationship("Contact", secondary=deal_contacts, back_populates="deals")
    companies = relationship("Company", secondary=deal_companies, back_populates="deals")
    
    # CRM Relationships
    activities = relationship("Activity", back_populates="deal")
    tasks = relationship("Task", back_populates="deal")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_deal_owner_stage', 'owner_id', 'stage'),
        Index('idx_deal_type_stage', 'deal_type', 'stage'),
        Index('idx_deal_active', 'is_active'),
        Index('idx_deal_close_date', 'expected_close_date'),
        CheckConstraint('probability >= 0 AND probability <= 100', name='check_deal_probability'),
    )

    def validate(self) -> None:
        """Custom validation for deal data."""
        super().validate()
        
        if not self.project_name or len(self.project_name.strip()) < 3:
            raise ValidationError("Project name must be at least 3 characters long.")
        
        if not self.owner_id:
            raise ValidationError("Deal must have an owner assigned.")
        
        if self.probability < 0 or self.probability > 100:
            raise ValidationError("Probability must be between 0 and 100.")
        
        if self.total_amount < 0:
            raise ValidationError("Total amount cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the deal instance to a dictionary."""
        data = super().to_dict()
        data['owner_name'] = self.owner.full_name if self.owner else None
        data['contact_count'] = len(self.contacts)
        data['company_count'] = len(self.companies)
        data['recipient_count'] = len(self.recipients)
        data['total_quotes_value'] = float(self.get_total_quotes_value())
        data['is_closed'] = self.stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]
        return data

    def get_total_quotes_value(self) -> Decimal:
        """Calculate total value of all quotes for this deal."""
        total = Decimal('0.0')
        for recipient in self.recipients:
            for quote in recipient.quotes:
                total += quote.total_price
        return total

    def get_latest_quote(self) -> Optional['Quote']:
        """Get the most recent quote for this deal."""
        latest_quote = None
        latest_date = None
        
        for recipient in self.recipients:
            for quote in recipient.quotes:
                if not latest_date or quote.created_at > latest_date:
                    latest_date = quote.created_at
                    latest_quote = quote
        
        return latest_quote

    def get_active_quotes(self) -> List['Quote']:
        """Get all active quotes for this deal."""
        quotes = []
        for recipient in self.recipients:
            quotes.extend(recipient.quotes)
        return quotes

    def can_be_edited_by(self, user) -> bool:
        """Check if a user can edit this deal."""
        if user.is_admin():
            return True
        if user.is_manager():
            return True
        if self.owner_id == user.id:
            return True
        return False

    def is_closed(self) -> bool:
        """Check if deal is closed (won or lost)."""
        return self.stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]

    def is_active_deal(self) -> bool:
        """Check if deal is still active (not closed)."""
        return not self.is_closed() and self.is_active

    def get_primary_company(self) -> Optional['Company']:
        """Get the primary company for this deal."""
        return self.companies[0] if self.companies else None

    def get_primary_contact(self) -> Optional['Contact']:
        """Get the primary contact for this deal."""
        return self.contacts[0] if self.contacts else None

    def update_total_amount(self) -> None:
        """Update the total amount based on latest quote."""
        latest_quote = self.get_latest_quote()
        if latest_quote:
            self.total_amount = latest_quote.total_price

class QuoteRecipient(BaseModel):
    """Model for managing quote recipients (companies receiving quotes)."""
    __tablename__ = 'quote_recipients'
    
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    
    # Additional fields
    contact_person = Column(String(120))
    delivery_method = Column(String(50), default='email')  # email, mail, hand_delivery
    special_instructions = Column(Text)
    
    # Relationships
    deal = relationship("Deal", back_populates="recipients")
    company = relationship("Company", back_populates="quote_streams")
    quotes = relationship("Quote", back_populates="recipient", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_quote_recipient_deal_company', 'deal_id', 'company_id'),
    )

class Quote(BaseModel):
    """Model for managing quotes within a deal."""
    __tablename__ = 'quotes'
    
    recipient_id = Column(Integer, ForeignKey('quote_recipients.id'), nullable=False, index=True)
    revision = Column(Integer, nullable=False, default=1)
    notes = Column(Text)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    
    # Additional fields
    valid_until = Column(db.DateTime)
    status = Column(String(20), default='draft', index=True)  # draft, sent, accepted, rejected
    total_discount = Column(Numeric(5, 2), default=0.0)
    
    # Relationships
    recipient = relationship("QuoteRecipient", back_populates="quotes")
    options = relationship("QuoteOption", back_populates="quote", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_quote_recipient_revision', 'recipient_id', 'revision'),
        Index('idx_quote_status', 'status'),
    )
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price of all options."""
        return sum(option.total_price for option in self.options)
    
    @property
    def grand_total(self) -> Decimal:
        """Calculate grand total including discounts."""
        subtotal = self.total_price
        discount_amount = subtotal * ((self.total_discount or Decimal('0')) / Decimal('100'))
        return subtotal - discount_amount

class QuoteOption(BaseModel):
    """Model for managing quote options within a quote."""
    __tablename__ = 'quote_options'
    
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False, index=True)
    name = Column(String(120), nullable=False, default="Main Option")
    freight_charge = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # Lead-time fields
    lead_time_value = Column(String(20), nullable=True)  # The value (e.g., "8" or "3-4")
    lead_time_unit = Column(String(10), nullable=True, default='weeks')  # 'weeks' or 'days'
    is_ex_stock_brisbane = Column(Boolean, default=False)  # Special option for ex-stock Brisbane
    
    # Additional fields
    description = Column(Text)
    is_recommended = Column(Boolean, default=False)
    
    # Relationships
    quote = relationship("Quote", back_populates="options")
    line_items = relationship("QuoteLineItem", back_populates="option", cascade="all, delete-orphan", order_by="QuoteLineItem.display_order")
    snapshots = relationship("QuoteSnapshot", back_populates="quote_option", cascade="all, delete-orphan", order_by="QuoteSnapshot.version_number.desc()")
    
    # Indexes
    __table_args__ = (
        Index('idx_quote_option_quote', 'quote_id'),
    )
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price including freight."""
        subtotal = sum(item.total_price for item in self.line_items)
        return subtotal + self.freight_charge
    
    @property
    def grand_total(self) -> Decimal:
        """Calculate grand total including quote-level discounts."""
        quote_discount = self.quote.total_discount or Decimal('0')
        subtotal = self.total_price
        discount_amount = subtotal * (quote_discount / Decimal('100'))
        return subtotal - discount_amount
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal of line items only."""
        return sum(item.total_price for item in self.line_items)
    
    @property
    def lead_time_display(self) -> str:
        """Get formatted lead-time display string."""
        if self.is_ex_stock_brisbane:
            return "Ex-Stock Brisbane"
        elif self.lead_time_value and self.lead_time_unit:
            return f"{self.lead_time_value} {self.lead_time_unit}"
        else:
            return "TBA"

class QuoteLineItem(BaseModel):
    """Model for individual line items within a quote option."""
    __tablename__ = 'quote_line_items'
    
    option_id = Column(Integer, ForeignKey('quote_options.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    
    quantity = Column(Integer, nullable=False, default=1)
    list_price = Column(Numeric(10, 2), nullable=True)  # Original list price before discount
    unit_price = Column(Numeric(10, 2), nullable=False)  # Final price after discount
    notes = Column(Text)
    discount = Column(Numeric(5, 2), nullable=False, default=0.0)
    display_order = Column(Integer, nullable=False, default=0)
    
    # Custom product fields (when product_id is null)
    custom_sku = Column(String(80))
    custom_name = Column(String(200))
    custom_description = Column(Text)
    
    # Assembly metadata (for pump assemblies - stores configuration as JSON)
    assembly_metadata = Column(Text, nullable=True)  # Stores JSON configuration for pump assemblies
    
    # Relationships
    option = relationship("QuoteOption", back_populates="line_items")
    product = relationship("Product")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_line_item_option_order', 'option_id', 'display_order'),
        CheckConstraint('quantity > 0', name='check_line_item_quantity'),
        CheckConstraint('unit_price >= 0', name='check_line_item_unit_price'),
        CheckConstraint('discount >= 0 AND discount <= 100', name='check_line_item_discount'),
    )
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this line item.
        Unit price already has discount applied, so just multiply by quantity.
        """
        return self.unit_price * self.quantity
    
    @property
    def product_name(self) -> str:
        """Get the product name (from product or custom)."""
        if self.product:
            return self.product.description
        return self.custom_name or "Custom Item"
    
    @property
    def product_sku(self) -> str:
        """Get the product SKU (from product or custom)."""
        if self.product:
            return self.product.item_no
        return self.custom_sku or "CUSTOM"
    
    def validate(self) -> None:
        """Custom validation for line item data."""
        super().validate()
        
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        
        if self.discount < 0 or self.discount > 100:
            raise ValidationError("Discount must be between 0 and 100.")
        
        # Either product_id or custom fields must be provided
        if not self.product_id and not self.custom_name:
            raise ValidationError("Either a product must be selected or custom name must be provided.")