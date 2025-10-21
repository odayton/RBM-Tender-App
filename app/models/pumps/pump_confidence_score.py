# app/models/pumps/pump_confidence_score.py

from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base_model import BaseModel


class PumpConfidenceScore(BaseModel):
    """
    Pre-calculated confidence scores for pump/duty point combinations
    Used for quick lookup and display of historical success rates
    """
    __tablename__ = 'pump_confidence_scores'
    
    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False, index=True)
    duty_point_id = Column(Integer, ForeignKey('pump_duty_points.id'), nullable=False, index=True)
    
    # Matching statistics
    selection_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    total_duty_point_selections = Column(Integer, default=0, nullable=False)
    
    # Confidence metrics
    confidence_score = Column(Numeric(5, 2))  # 0-100 percentage
    confidence_stars = Column(Integer)  # 1-5 star rating
    
    # Match quality
    flow_rate_match_percentage = Column(Numeric(5, 2))
    head_pressure_match_percentage = Column(Numeric(5, 2))
    overall_match_quality = Column(Numeric(5, 2))
    
    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pump = relationship("Pump", back_populates="confidence_scores")
    duty_point = relationship("PumpDutyPoint", back_populates="confidence_scores")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('pump_id', 'duty_point_id', name='uq_pump_duty_point'),
        Index('idx_confidence_pump', 'pump_id'),
        Index('idx_confidence_duty_point', 'duty_point_id'),
        Index('idx_confidence_score', 'confidence_score'),
        CheckConstraint('selection_count >= 0', name='check_selection_count'),
        CheckConstraint('success_count >= 0', name='check_success_count'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 100 OR confidence_score IS NULL', 
                       name='check_confidence_score_range'),
        CheckConstraint('confidence_stars >= 1 AND confidence_stars <= 5 OR confidence_stars IS NULL', 
                       name='check_confidence_stars_range'),
    )
    
    def __repr__(self):
        return f"<ConfidenceScore Pump:{self.pump_id} Duty:{self.duty_point_id} Score:{self.confidence_score}%>"
    
    def calculate_confidence(self):
        """
        Calculate confidence score based on historical data
        
        Scoring factors:
        - 40% Selection Frequency
        - 30% Success Rate
        - 30% Match Quality
        """
        if self.total_duty_point_selections == 0:
            self.confidence_score = 0
            self.confidence_stars = 1
            return
        
        # Calculate relative frequency (how often THIS pump vs others)
        relative_frequency = (self.selection_count / self.total_duty_point_selections 
                            if self.total_duty_point_selections > 0 else 0)
        
        # Calculate success rate
        success_rate = (self.success_count / self.selection_count 
                       if self.selection_count > 0 else 0)
        
        # Use match quality or default to 0.8
        match_quality = float(self.overall_match_quality) / 100 if self.overall_match_quality else 0.8
        
        # Weighted confidence score (0-100)
        confidence = (
            (relative_frequency * 40) +
            (success_rate * 30) +
            (match_quality * 30)
        ) * 100
        
        self.confidence_score = round(confidence, 2)
        self.confidence_stars = self._calculate_star_rating(confidence)
        self.last_calculated_at = datetime.utcnow()
    
    def _calculate_star_rating(self, confidence_score):
        """Convert confidence score to 1-5 star rating"""
        if confidence_score >= 90:
            return 5
        elif confidence_score >= 75:
            return 4
        elif confidence_score >= 50:
            return 3
        elif confidence_score >= 25:
            return 2
        else:
            return 1

