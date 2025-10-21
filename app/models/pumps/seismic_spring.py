# app/models/pumps/seismic_spring.py

from sqlalchemy import Column, String, Text, Numeric, Boolean, Index, CheckConstraint
from app.models.base_model import BaseModel


class SeismicSpring(BaseModel):
    """
    Seismic springs for vibration isolation
    Supports both standard and 50mm static springs
    """
    __tablename__ = 'seismic_springs'
    
    part_number = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Specifications (all optional)
    max_load_kg = Column(Numeric(8, 2))
    static_deflection_mm = Column(Numeric(8, 2))
    spring_constant = Column(Numeric(10, 4))
    stripe_1_color = Column(String(50))
    stripe_2_color = Column(String(50))
    
    # Pricing (optional)
    list_price = Column(Numeric(10, 2))
    nett_price = Column(Numeric(10, 2))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('max_load_kg >= 0 OR max_load_kg IS NULL', name='check_spring_max_load'),
        CheckConstraint('list_price >= 0 OR list_price IS NULL', name='check_spring_list_price'),
        CheckConstraint('nett_price >= 0 OR nett_price IS NULL', name='check_spring_nett_price'),
        Index('idx_spring_part_number', 'part_number'),
    )
    
    def __repr__(self):
        return f"<SeismicSpring {self.part_number}: {self.description}>"

