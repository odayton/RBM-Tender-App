# app/models/pumps/crossbar.py

from sqlalchemy import Column, String, Text, Numeric, Boolean, Index, CheckConstraint
from app.models.base_model import BaseModel


class Crossbar(BaseModel):
    """
    Crossbars as alternative mounting solution
    """
    __tablename__ = 'crossbars'
    
    sku = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Pricing (optional)
    list_price = Column(Numeric(10, 2))
    nett_price = Column(Numeric(10, 2))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('list_price >= 0 OR list_price IS NULL', name='check_crossbar_list_price'),
        CheckConstraint('nett_price >= 0 OR nett_price IS NULL', name='check_crossbar_nett_price'),
        Index('idx_crossbar_sku', 'sku'),
    )
    
    def __repr__(self):
        return f"<Crossbar {self.sku}: {self.description}>"

