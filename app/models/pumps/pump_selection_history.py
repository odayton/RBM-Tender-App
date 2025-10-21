# app/models/pumps/pump_selection_history.py

from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, Boolean, Index
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class PumpSelectionHistory(BaseModel):
    """
    Tracks every pump selection for duty points
    Builds historical data for confidence scoring
    """
    __tablename__ = 'pump_selection_history'
    
    duty_point_id = Column(Integer, ForeignKey('pump_duty_points.id'), nullable=False, index=True)
    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False, index=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=True)
    option_id = Column(Integer, ForeignKey('quote_options.id'), nullable=True)
    
    # Duty point details at time of selection
    flow_rate_lps = Column(Numeric(8, 2), nullable=False)
    head_pressure_kpa = Column(Numeric(8, 2), nullable=False)
    
    # Pump specs at time of selection
    pump_kw_rating = Column(Numeric(8, 2))
    pump_poles = Column(Integer)
    
    # Selection metadata
    selected_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    selection_reason = Column(Text)
    was_successful = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    duty_point = relationship("PumpDutyPoint", back_populates="selection_history")
    pump = relationship("Pump", back_populates="selection_history")
    quote = relationship("Quote")
    option = relationship("QuoteOption")
    selected_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_selection_duty_pump', 'duty_point_id', 'pump_id'),
        Index('idx_selection_pump', 'pump_id'),
        Index('idx_selection_quote', 'quote_id'),
    )
    
    def __repr__(self):
        return f"<PumpSelectionHistory Pump:{self.pump_id} DutyPoint:{self.duty_point_id}>"

