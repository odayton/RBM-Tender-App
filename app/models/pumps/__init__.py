"""
Pump Models Package
Placeholder/stub models until full implementation
"""

# TODO: Implement full pump models
# These are minimal stubs to prevent import errors

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base_model import BaseModel

class PumpSeries(BaseModel):
    """Stub model for Pump Series"""
    __tablename__ = 'pump_series'
    series_code = Column(String(50))
    series_name = Column(String(200))
    is_active = Column(Boolean, default=True)

class Pump(BaseModel):
    """Stub model for Pump"""
    __tablename__ = 'pumps'
    part_number = Column(String(100))
    name = Column(String(200))
    series_id = Column(Integer, ForeignKey('pump_series.id'))
    list_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    series = relationship("PumpSeries")

class PumpComponent(BaseModel):
    """Stub model for Pump Component"""
    __tablename__ = 'pump_components'
    component_type = Column(String(50))
    part_number = Column(String(100))
    description = Column(Text)
    list_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)

class PumpBOM(BaseModel):
    """Stub model for Pump BOM"""
    __tablename__ = 'pump_bom'
    pump_id = Column(Integer, ForeignKey('pumps.id'))
    component_type = Column(String(50))
    component_id = Column(Integer)
    quantity = Column(Integer)
    is_optional = Column(Boolean, default=False)
    pump = relationship("Pump")

class InertiaBase(BaseModel):
    """Stub model for Inertia Base"""
    __tablename__ = 'inertia_bases'
    part_number = Column(String(100))
    description = Column(Text)
    list_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)

class SeismicSpring(BaseModel):
    """Stub model for Seismic Spring"""
    __tablename__ = 'seismic_springs'
    part_number = Column(String(100))
    description = Column(Text)
    max_load_kg = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)

class RubberMount(BaseModel):
    """Stub model for Rubber Mount"""
    __tablename__ = 'rubber_mounts'
    sku = Column(String(100))
    item_description = Column(Text)
    list_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)

class Crossbar(BaseModel):
    """Stub model for Crossbar"""
    __tablename__ = 'crossbars'
    sku = Column(String(100))
    description = Column(Text)
    list_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)

class MotorProtection(BaseModel):
    """Stub model for Motor Protection"""
    __tablename__ = 'motor_protection'
    description = Column(Text)
    nett_cost = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)

class DripTripTray(BaseModel):
    """Stub model for Drip Trip Tray"""
    __tablename__ = 'drip_trip_trays'
    series_id = Column(Integer, ForeignKey('pump_series.id'))
    description = Column(Text)
    nett_cost = Column(Numeric(10, 2))
    is_standard = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    series = relationship("PumpSeries")

class PumpDutyPoint(BaseModel):
    """Stub model for Pump Duty Point"""
    __tablename__ = 'pump_duty_points'
    flow_rate_lps = Column(Numeric(10, 2))
    head_pressure_kpa = Column(Numeric(10, 2))
    series_id = Column(Integer, ForeignKey('pump_series.id'))
    tolerance_percentage = Column(Numeric(5, 2))
    series = relationship("PumpSeries")

class PumpSelectionHistory(BaseModel):
    """Stub model for Pump Selection History"""
    __tablename__ = 'pump_selection_history'
    pump_id = Column(Integer, ForeignKey('pumps.id'))
    pump = relationship("Pump")

class PumpConfidenceScore(BaseModel):
    """Stub model for Pump Confidence Score"""
    __tablename__ = 'pump_confidence_scores'
    pump_id = Column(Integer, ForeignKey('pumps.id'))
    score = Column(Numeric(5, 2))
    pump = relationship("Pump")

__all__ = [
    'PumpSeries', 'Pump', 'PumpComponent', 'PumpBOM',
    'InertiaBase', 'SeismicSpring', 'RubberMount', 'Crossbar',
    'MotorProtection', 'DripTripTray',
    'PumpDutyPoint', 'PumpSelectionHistory', 'PumpConfidenceScore'
]

