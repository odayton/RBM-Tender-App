from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..base_model import BaseModel
from app.core.core_errors import ValidationError
# Import the association table from its new, dedicated file
from ..deals.deal_associations import deal_customers

class Customer(BaseModel):
    """Model for managing customer information"""
    __tablename__ = 'customers'
    
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone_number = Column(String(20))
    position = Column(String(100))
    
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    company = relationship("Company", back_populates="contacts")
    quotes = relationship("Quote", back_populates="customer")
    
    # This relationship now uses the cleanly imported association table
    deals = relationship("Deal", secondary=deal_customers, back_populates="customers")

    def validate(self) -> None:
        """Validate customer data"""
        super().validate()
        if not '@' in self.email:
            raise ValidationError("Invalid email format")
        if self.phone_number and not self.phone_number.replace('+', '').replace(' ', '').isdigit():
            raise ValidationError("Phone number should contain only digits, spaces, and '+'")