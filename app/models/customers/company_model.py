from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from ..base_model import BaseModel
from ..deals.deal_associations import deal_companies

class Company(BaseModel):
    """Model for managing companies."""
    __tablename__ = 'companies'

    company_name = Column(String(120), unique=True, nullable=False, index=True)
    address = Column(Text)
    # ... other columns

    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    deals = relationship("Deal", secondary=deal_companies, back_populates="companies")
    
    # NEW: Relationship to the quote streams this company is a part of
    quote_streams = relationship("QuoteRecipient", back_populates="company")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.company_name}')>"