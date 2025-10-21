from sqlalchemy import Column, String, Text, Boolean, Index
from sqlalchemy.orm import relationship
from typing import Dict, Any, List
from ..base_model import BaseModel
from ..deals.deal_associations import deal_companies
from ...core.core_errors import ValidationError

class Company(BaseModel):
    """Model for managing companies."""
    __tablename__ = 'companies'

    company_name = Column(String(120), unique=True, nullable=False, index=True)
    phone_number = Column(String(30))
    domain = Column(String(100), index=True)  # Company email domain for auto-assignment
    is_active = Column(Boolean, default=True, nullable=False)  # Track active/inactive companies
    
    # Relationships
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    deals = relationship("Deal", secondary=deal_companies, back_populates="companies")
    quote_streams = relationship("QuoteRecipient", back_populates="company")
    
    # CRM Relationships
    activities = relationship("Activity", back_populates="company")
    tasks = relationship("Task", back_populates="company")

    # Indexes for performance
    __table_args__ = (
        Index('idx_company_domain', 'domain'),
    )

    def validate(self) -> None:
        """Custom validation for company data."""
        super().validate()
        
        if not self.company_name or len(self.company_name.strip()) < 2:
            raise ValidationError("Company name must be at least 2 characters long.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the company instance to a dictionary."""
        data = super().to_dict()
        data['contact_count'] = len(self.contacts)
        data['deal_count'] = len(self.deals)
        data['active_contacts_count'] = len([c for c in self.contacts if c.is_active])
        data['active_deals_count'] = len([d for d in self.deals if d.stage.value not in ['CLOSED_LOST', 'CLOSED_WON']])
        return data

    def get_primary_contact(self):
        """Get the primary contact for this company."""
        return self.contacts[0] if self.contacts else None

    def get_active_contacts(self) -> List['Contact']:
        """Get all active contacts for this company."""
        return [contact for contact in self.contacts if contact.is_active]

    def get_active_deals(self) -> List['Deal']:
        """Get all active deals for this company."""
        from ..deals.deal_types import DealStage
        active_stages = [DealStage.SALES_LEAD, DealStage.TENDER, DealStage.PROPOSAL, DealStage.NEGOTIATION]
        return [deal for deal in self.deals if deal.stage in active_stages]

    def get_total_deal_value(self) -> float:
        """Calculate total value of all deals for this company."""
        return sum(deal.total_amount for deal in self.deals)

    def has_active_deals(self) -> bool:
        """Check if company has any active deals."""
        return len(self.get_active_deals()) > 0

    def is_engaged(self) -> bool:
        """Check if company is actively engaged (has active deals or recent activity)."""
        return self.has_active_deals() or len(self.get_active_contacts()) > 0

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.company_name}')>"