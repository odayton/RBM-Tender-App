from typing import Dict, Any
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class Company(BaseModel):
    """
    Represents a client company in the database.
    Inherits id, created_at, and updated_at from BaseModel.
    """
    __tablename__ = 'companies'
    
    # --- Columns ---
    company_name = Column(String(120), nullable=False, unique=True, index=True)
    address = Column(String(255))
    
    # --- Relationships ---
    # One-to-many relationship with Customer (contacts)
    # When a Company is deleted, all its associated Contacts are also deleted.
    contacts = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    
    # Many-to-many relationship with Deal
    deals = relationship("DealCompany", back_populates="company", cascade="all, delete-orphan")

    def validate(self) -> None:
        """Custom validation for company data."""
        super().validate()
        
        if not self.company_name:
            raise ValidationError("Company name is required.")

        if len(self.company_name) < 2:
            raise ValidationError("Company name must be at least 2 characters long.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the company instance to a dictionary."""
        data = super().to_dict()
        data.update({
            'contact_count': len(self.contacts),
            'deal_count': len(self.deals)
        })
        return data

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.company_name}')>"