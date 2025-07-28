from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from typing import Dict, Any
from ..base_model import BaseModel
from ..deals.deal_associations import deal_companies
from ...core.core_errors import ValidationError

class Company(BaseModel):
    """Model for managing companies."""
    __tablename__ = 'companies'

    company_name = Column(String(120), unique=True, nullable=False, index=True)
    address = Column(Text)

    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    deals = relationship("Deal", secondary=deal_companies, back_populates="companies")
    
    # NEW: Relationship to the quote streams this company is a part of
    quote_streams = relationship("QuoteRecipient", back_populates="company")

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
        return data

    def get_primary_contact(self):
        """Get the primary contact for this company."""
        return self.contacts[0] if self.contacts else None

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.company_name}')>"