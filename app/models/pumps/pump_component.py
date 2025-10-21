# app/models/pumps/pump_component.py

from sqlalchemy import Column, String, Text, Numeric, Boolean, Index
from app.models.base_model import BaseModel


class PumpComponent(BaseModel):
    """
    Generic pump components (accessories)
    Flexible model for various component types
    """
    __tablename__ = 'pump_components'
    
    component_type = Column(String(50), nullable=False, index=True)
    part_number = Column(String(100))
    description = Column(Text)
    specifications = Column(Text)  # JSON string for flexible data
    list_price = Column(Numeric(10, 2))
    nett_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_component_type_active', 'component_type', 'is_active'),
        Index('idx_component_part_number', 'part_number'),
    )
    
    def __repr__(self):
        return f"<PumpComponent {self.component_type}: {self.description}>"

