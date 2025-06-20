from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship, validates
import re

from ..base_model import BaseModel
from ...core.core_errors import ValidationError

class Company(BaseModel):
    """Model for managing companies."""
    __tablename__ = 'companies'

    company_name = Column(String(120), unique=True, nullable=False, index=True)
    address = Column(Text)
    phone_number = Column(String(30))
    website = Column(String(255))

    # This relationship was pointing to the old 'Customer' name.
    # It has now been corrected to 'Contact'.
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    
    # This relationship links a company to all the deals associated with it.
    deals = relationship("Deal", back_populates="company")

    def validate(self) -> None:
        """Custom validation for company data."""
        super().validate()
        if not self.company_name:
            raise ValidationError("Company name cannot be empty.")
            
        if self.website:
            # Simple regex for basic URL validation
            url_pattern = re.compile(
                r'^(https?://)?'  # http:// or https://
                r'((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|'  # domain name
                r'((\d{1,3}\.){3}\d{1,3}))'  # or ip
                r'(\:\d+)?(/[-a-z\d%_.~+]*)*'  # port and path
                r'(\?[;&a-z\d%_.~+=-]*)?'  # query string
                r'(\#[-a-z\d_]*)?$', re.IGNORECASE)
            if not re.match(url_pattern, self.website):
                raise ValidationError(f"Invalid website URL format for '{self.website}'.")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.company_name}')>"