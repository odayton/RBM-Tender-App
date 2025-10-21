# app/models/pumps/rubber_mount.py

from sqlalchemy import Column, String, Text, Numeric, Boolean, Index, CheckConstraint
from app.models.base_model import BaseModel


class RubberMount(BaseModel):
    """
    Rubber mounts for vibration isolation
    """
    __tablename__ = 'rubber_mounts'
    
    sku = Column(String(100), nullable=False, unique=True, index=True)
    item_description = Column(Text)
    static_deflection_mm = Column(Numeric(8, 2))
    
    # Pricing (optional)
    list_price = Column(Numeric(10, 2))
    nett_price = Column(Numeric(10, 2))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('list_price >= 0 OR list_price IS NULL', name='check_mount_list_price'),
        CheckConstraint('nett_price >= 0 OR nett_price IS NULL', name='check_mount_nett_price'),
        Index('idx_mount_sku', 'sku'),
    )
    
    def __repr__(self):
        return f"<RubberMount {self.sku}: {self.item_description}>"

