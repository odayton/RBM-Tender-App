# app/models/pumps/pump_duty_point.py

from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class PumpDutyPoint(BaseModel):
    """
    Historical duty points for intelligent pump selection
    Tracks flow rate and head pressure combinations
    """
    __tablename__ = 'pump_duty_points'
    
    flow_rate_lps = Column(Numeric(8, 2), nullable=False)
    head_pressure_kpa = Column(Numeric(8, 2), nullable=False)
    series_id = Column(Integer, ForeignKey('pump_series.id'), nullable=True, index=True)
    tolerance_percentage = Column(Numeric(5, 2), default=5.0, nullable=False)
    notes = Column(Text)
    
    # Relationships
    series = relationship("PumpSeries")
    selection_history = relationship("PumpSelectionHistory", back_populates="duty_point")
    confidence_scores = relationship("PumpConfidenceScore", back_populates="duty_point")
    
    # Indexes
    __table_args__ = (
        Index('idx_duty_point_flow_head', 'flow_rate_lps', 'head_pressure_kpa'),
        Index('idx_duty_point_series', 'series_id'),
        CheckConstraint('flow_rate_lps > 0', name='check_duty_flow_rate'),
        CheckConstraint('head_pressure_kpa > 0', name='check_duty_head_pressure'),
        CheckConstraint('tolerance_percentage > 0', name='check_duty_tolerance'),
    )
    
    def __repr__(self):
        return f"<DutyPoint {self.flow_rate_lps}L/s @ {self.head_pressure_kpa}kPa>"
    
    def matches(self, flow_rate, head_pressure, tolerance=None):
        """Check if this duty point matches given parameters within tolerance"""
        tol = float(tolerance if tolerance is not None else self.tolerance_percentage)
        
        flow_min = float(self.flow_rate_lps) * (1 - tol / 100)
        flow_max = float(self.flow_rate_lps) * (1 + tol / 100)
        head_min = float(self.head_pressure_kpa) * (1 - tol / 100)
        head_max = float(self.head_pressure_kpa) * (1 + tol / 100)
        
        flow_matches = flow_min <= float(flow_rate) <= flow_max
        head_matches = head_min <= float(head_pressure) <= head_max
        
        return flow_matches and head_matches

