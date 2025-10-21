# app/models/pumps/drip_trip_tray.py

from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, Boolean, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class DripTripTray(BaseModel):
    """
    Drip trip trays - cost varies by pump series
    """
    __tablename__ = 'drip_trip_trays'
    
    series_id = Column(Integer, ForeignKey('pump_series.id'), nullable=False, index=True)
    description = Column(String(200), nullable=False)
    nett_cost = Column(Numeric(10, 2), nullable=False)
    is_standard = Column(Boolean, default=False, nullable=False)  # Standard for this series
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    series = relationship("PumpSeries", back_populates="drip_trip_trays")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('nett_cost >= 0', name='check_drip_tray_cost'),
        Index('idx_drip_tray_series', 'series_id'),
    )
    
    def __repr__(self):
        return f"<DripTripTray Series:{self.series_id} - ${self.nett_cost}>"

