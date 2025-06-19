from typing import Dict, Any
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base_model import BaseModel
from app.core.core_errors import ValidationError

class Company(BaseModel):
    """Model for managing companies"""
    __tablename__ = 'companies'
    
    company_name = Column(String(100), nullable=False, unique=True)
    address = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contacts = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="company")

    def validate(self) -> None:
        """Validate company data"""
        super().validate()
        
        if not self.company_name:
            raise ValidationError("Company name is required")

        if len(self.company_name) < 2:
            raise ValidationError("Company name must be at least 2 characters")

    def to_dict(self) -> Dict[str, Any]:
        """Convert company to dictionary"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'contact_count': len(self.contacts) if self.contacts else 0,
            'deal_count': len(self.deals) if self.deals else 0
        }

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.company_name}')>"