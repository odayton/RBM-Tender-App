# app/models/pumps/pump_bom.py

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Index
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class PumpBOM(BaseModel):
    """
    Bill of Materials - Links pumps to their components
    Tracks which components are needed for each pump
    """
    __tablename__ = 'pump_bom'
    
    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False, index=True)
    component_id = Column(Integer, nullable=False)  # Links to various component tables
    component_type = Column(String(50), nullable=False)  # inertia_base, spring, rubber_mount, crossbar
    quantity = Column(Integer, default=1, nullable=False)
    is_optional = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    pump = relationship("Pump", back_populates="bom_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_pump_bom_pump', 'pump_id'),
        Index('idx_pump_bom_component', 'component_type', 'component_id'),
    )
    
    def __repr__(self):
        return f"<PumpBOM Pump:{self.pump_id} {self.component_type}:{self.component_id} x{self.quantity}>"

