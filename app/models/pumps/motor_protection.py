# app/models/pumps/motor_protection.py

from sqlalchemy import Column, Text, Numeric, Boolean, CheckConstraint
from app.models.base_model import BaseModel


class MotorProtection(BaseModel):
    """
    Motor protection accessories
    """
    __tablename__ = 'motor_protection'
    
    description = Column(Text, nullable=False)
    nett_cost = Column(Numeric(10, 2), nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('nett_cost >= 0', name='check_motor_protection_cost'),
    )
    
    def __repr__(self):
        return f"<MotorProtection: {self.description} - ${self.nett_cost}>"

