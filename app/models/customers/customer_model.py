import re
from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..base_model import BaseModel
from ...core.core_errors import ValidationError
from ..deals.deal_associations import deal_contacts

class Contact(BaseModel):
    """Model for managing contacts (people) associated with companies."""
    __tablename__ = 'contacts'

    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True, index=True)
    phone_number = Column(String(30))
    position = Column(String(120))
    
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    
    # --- Relationships ---
    company = relationship("Company", back_populates="contacts")
    
    # This relationship allows a Contact to be associated with multiple Deals
    deals = relationship("Deal", secondary=deal_contacts, back_populates="contacts")
    
    def validate(self) -> None:
        """Custom validation for contact data."""
        super().validate()
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not self.email or not re.match(email_pattern, self.email):
            raise ValidationError(f"Invalid email format for '{self.email}'.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the contact instance to a dictionary."""
        data = super().to_dict()
        if self.company:
            data['company_name'] = self.company.company_name
        return data

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.name}')>"