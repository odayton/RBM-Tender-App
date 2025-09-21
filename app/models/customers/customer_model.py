import re
from typing import Dict, Any, List
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship

from ..base_model import BaseModel
from ...core.core_errors import ValidationError
from ..deals.deal_associations import deal_contacts

class Contact(BaseModel):
    """Model for managing contacts (people) associated with companies."""
    __tablename__ = 'contacts'

    name = Column(String(120), nullable=False, index=True)
    email = Column(String(120), nullable=False, unique=True, index=True)
    phone_number = Column(String(30))
    mobile_number = Column(String(30))
    position = Column(String(120), nullable=True)
    department = Column(String(100))
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(500))
    
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="contacts")
    deals = relationship("Deal", secondary=deal_contacts, back_populates="contacts")
    
    # CRM Relationships
    activities = relationship("Activity", back_populates="contact")
    tasks = relationship("Task", back_populates="contact")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_contact_company_active', 'company_id', 'is_active'),
        Index('idx_contact_primary', 'company_id', 'is_primary'),
        Index('idx_contact_name_email', 'name', 'email'),
    )

    def validate(self) -> None:
        """Custom validation for contact data."""
        super().validate()
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError("Contact name must be at least 2 characters long.")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not self.email or not re.match(email_pattern, self.email):
            raise ValidationError(f"Invalid email format for '{self.email}'.")
        
        if self.phone_number and not re.match(r'^[\d\s\-\+\(\)]+$', self.phone_number):
            raise ValidationError("Phone number contains invalid characters.")
        
        if self.mobile_number and not re.match(r'^[\d\s\-\+\(\)]+$', self.mobile_number):
            raise ValidationError("Mobile number contains invalid characters.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the contact instance to a dictionary."""
        data = super().to_dict()
        if self.company:
            data['company_name'] = self.company.company_name
        data['deal_count'] = len(self.deals)
        data['active_deals_count'] = len([d for d in self.deals if d.stage.value not in ['CLOSED_LOST', 'CLOSED_WON']])
        return data

    def get_full_info(self) -> str:
        """Get full contact information as a string."""
        info_parts = [self.name]
        if self.position:
            info_parts.append(f"({self.position})")
        if self.company:
            info_parts.append(f"at {self.company.company_name}")
        return " ".join(info_parts)

    def get_active_deals(self) -> List['Deal']:
        """Get all active deals for this contact."""
        from ..deals.deal_types import DealStage
        active_stages = [DealStage.SALES_LEAD, DealStage.TENDER, DealStage.PROPOSAL, DealStage.NEGOTIATION]
        return [deal for deal in self.deals if deal.stage in active_stages]

    def get_total_deal_value(self) -> float:
        """Calculate total value of all deals for this contact."""
        return sum(deal.total_amount for deal in self.deals)

    def has_active_deals(self) -> bool:
        """Check if contact has any active deals."""
        return len(self.get_active_deals()) > 0

    def is_engaged(self) -> bool:
        """Check if contact is actively engaged (has active deals)."""
        return self.has_active_deals()

    def set_as_primary(self) -> None:
        """Set this contact as the primary contact for their company."""
        # Remove primary status from other contacts in the same company
        for contact in self.company.contacts:
            if contact.id != self.id:
                contact.is_primary = False
        
        # Set this contact as primary
        self.is_primary = True

    def get_preferred_phone(self) -> str:
        """Get the preferred phone number (mobile first, then phone)."""
        return self.mobile_number or self.phone_number or ""

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}', company='{self.company.company_name if self.company else 'None'}', active={self.is_active})>"