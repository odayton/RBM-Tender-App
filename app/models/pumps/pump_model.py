# app/models/pumps/pump_model.py

from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, Boolean, Index, CheckConstraint
from sqlalchemy.orm import relationship
from decimal import Decimal
from app.models.base_model import BaseModel


class Pump(BaseModel):
    """
    Model for pump products
    
    Required fields:
    - part_number: Manufacturer part number
    - name: Pump description/name
    
    All other fields are optional to support partially configured pumps
    """
    __tablename__ = 'pumps'
    
    # Basic info (REQUIRED)
    part_number = Column(String(100), nullable=False, index=True)
    name = Column(Text, nullable=False)
    
    # Series relationship (OPTIONAL - pump may not have series assigned yet)
    series_id = Column(Integer, ForeignKey('pump_series.id'), nullable=True, index=True)
    
    # Additional identifiers (OPTIONAL)
    item_number = Column(String(100), index=True)
    description = Column(Text)
    
    # Technical specifications (OPTIONAL)
    kw_rating = Column(Numeric(8, 2))
    poles = Column(Integer)
    
    # Performance characteristics (OPTIONAL - for duty point matching)
    min_flow_rate_lps = Column(Numeric(8, 2))
    max_flow_rate_lps = Column(Numeric(8, 2))
    optimal_flow_rate_lps = Column(Numeric(8, 2))
    min_head_pressure_kpa = Column(Numeric(8, 2))
    max_head_pressure_kpa = Column(Numeric(8, 2))
    optimal_head_pressure_kpa = Column(Numeric(8, 2))
    
    # Pump curve link (OPTIONAL)
    model_slug = Column(String(100))
    pump_curve_url = Column(String(500))
    
    # Pricing (OPTIONAL)
    list_price = Column(Numeric(10, 2))
    nett_price = Column(Numeric(10, 2))
    ip56_list_price = Column(Numeric(10, 2))
    ip56_nett_price = Column(Numeric(10, 2))
    ip66_list_price = Column(Numeric(10, 2))
    ip66_nett_price = Column(Numeric(10, 2))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    series = relationship("PumpSeries", back_populates="pumps")
    bom_items = relationship("PumpBOM", back_populates="pump", cascade="all, delete-orphan")
    selection_history = relationship("PumpSelectionHistory", back_populates="pump")
    confidence_scores = relationship("PumpConfidenceScore", back_populates="pump")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_pump_part_number', 'part_number'),
        Index('idx_pump_series_active', 'series_id', 'is_active'),
        Index('idx_pump_name', 'name'),  # For search
        CheckConstraint('kw_rating >= 0 OR kw_rating IS NULL', name='check_pump_kw_rating'),
        CheckConstraint('poles > 0 OR poles IS NULL', name='check_pump_poles'),
        CheckConstraint('list_price >= 0 OR list_price IS NULL', name='check_pump_list_price'),
        CheckConstraint('nett_price >= 0 OR nett_price IS NULL', name='check_pump_nett_price'),
    )
    
    def __repr__(self):
        return f"<Pump {self.part_number}: {self.name}>"
    
    @property
    def display_name(self):
        """Get display name for UI"""
        if self.item_number:
            return f"{self.item_number} - {self.name}"
        return self.name
    
    @property
    def has_pump_curve(self):
        """Check if pump curve URL is available"""
        return bool(self.pump_curve_url or (self.series and self.series.series_path and self.part_number))
    
    def get_pump_curve_url(self):
        """
        Get or generate pump curve URL
        Returns stored URL or generates from series configuration
        """
        if self.pump_curve_url:
            return self.pump_curve_url
        
        if self.series and self.part_number:
            return self.series.generate_pump_curve_url(self.name, self.part_number)
        
        return None
    
    def matches_duty_point(self, flow_rate_lps, head_pressure_kpa, tolerance=5.0):
        """
        Check if pump matches given duty point within tolerance
        
        Args:
            flow_rate_lps: Required flow rate in L/s
            head_pressure_kpa: Required head pressure in kPa
            tolerance: Tolerance percentage (default 5%)
        
        Returns:
            Boolean indicating if pump matches
        """
        if not all([self.min_flow_rate_lps, self.max_flow_rate_lps, 
                   self.min_head_pressure_kpa, self.max_head_pressure_kpa]):
            return False
        
        # Calculate tolerance ranges
        flow_min = float(flow_rate_lps) * (1 - tolerance / 100)
        flow_max = float(flow_rate_lps) * (1 + tolerance / 100)
        head_min = float(head_pressure_kpa) * (1 - tolerance / 100)
        head_max = float(head_pressure_kpa) * (1 + tolerance / 100)
        
        # Check if pump's range overlaps with required range
        flow_matches = (float(self.min_flow_rate_lps) <= flow_max and 
                       float(self.max_flow_rate_lps) >= flow_min)
        head_matches = (float(self.min_head_pressure_kpa) <= head_max and 
                       float(self.max_head_pressure_kpa) >= head_min)
        
        return flow_matches and head_matches

