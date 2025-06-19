from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from ..base_model import BaseModel
from app.core.core_errors import ValidationError
import enum

class PumpSeries(enum.Enum):
    """Enum for different pump series"""
    NBG = "NBG"
    CR = "CR"
    TP = "TP"
    CM = "CM"
    MAGNA = "MAGNA"
    UPS = "UPS"
    CRE = "CRE"
    TPE = "TPE"
    NK = "NK"

class Pump(BaseModel):
    """Base model for all pump series"""
    __tablename__ = 'pumps'

    model_number = Column(String(50), unique=True, nullable=False, index=True)
    series = Column(Enum(PumpSeries), nullable=False)
    frame_size = Column(String(50))
    poles = Column(Integer)
    power_kw = Column(Float)
    ie_class = Column(String(10))
    flow_rate = Column(Float)
    head = Column(Float)
    efficiency = Column(Float)
    
    ip_ratings = relationship("PumpIPRating", back_populates="pump", cascade="all, delete-orphan")
    specifications = Column(JSON)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.specifications = kwargs.get('specifications', {})

    def validate(self) -> None:
        """Validate pump data"""
        super().validate()
        if not self.model_number:
            raise ValidationError("Model number is required")
        if not self.series:
            raise ValidationError("Pump series is required")
        self._validate_series_specific()
    
    def _validate_series_specific(self) -> None:
        """Series-specific validation rules"""
        if self.series == PumpSeries.NBG:
            if not self.frame_size:
                raise ValidationError("Frame size is required for NBG series")

    def __repr__(self) -> str:
        return f"<Pump(series='{self.series.value}', model='{self.model_number}')>"

class PumpIPRating(BaseModel):
    """Model for pump IP ratings"""
    __tablename__ = 'pump_ip_ratings'
    
    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False)
    rating = Column(String(10), nullable=False)
    
    pump = relationship("Pump", back_populates="ip_ratings")

    def __repr__(self) -> str:
        return f"<PumpIPRating(pump_id={self.pump_id}, rating='{self.rating}')>"