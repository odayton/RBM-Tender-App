# app/models/pumps/inertia_base.py

from sqlalchemy import Column, String, Numeric, Integer, Boolean, Index, CheckConstraint
from app.models.base_model import BaseModel


class InertiaBase(BaseModel):
    """
    Inertia bases for pump mounting
    Stores dimensions and specifications
    """
    __tablename__ = 'inertia_bases'
    
    part_number = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(200))
    
    # Dimensions (all optional)
    weight_kg = Column(Numeric(8, 3))
    length_mm = Column(Integer)
    width_mm = Column(Integer)
    depth_mm = Column(Integer)
    mount_height_mm = Column(Integer)
    
    # Pricing (optional)
    list_price = Column(Numeric(10, 2))
    nett_cost = Column(Numeric(10, 2))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('weight_kg >= 0 OR weight_kg IS NULL', name='check_inertia_weight'),
        CheckConstraint('list_price >= 0 OR list_price IS NULL', name='check_inertia_list_price'),
        CheckConstraint('nett_cost >= 0 OR nett_cost IS NULL', name='check_inertia_nett_cost'),
        Index('idx_inertia_part_number', 'part_number'),
    )
    
    def __repr__(self):
        dims = f"{self.length_mm}x{self.width_mm}x{self.depth_mm}" if self.length_mm else "unknown"
        return f"<InertiaBase {self.part_number}: {dims}>"
    
    @property
    def dimensions_display(self):
        """Get formatted dimensions string"""
        if self.length_mm and self.width_mm and self.depth_mm:
            return f"{self.length_mm} x {self.width_mm} x {self.depth_mm}"
        return "Dimensions not specified"

