from sqlalchemy import (
    Column, String, Integer, ForeignKey, Float, Text, Enum as PyEnum
)
from sqlalchemy.orm import relationship
from ..base_model import BaseModel
from enum import Enum

class PumpIPRating(Enum):
    """Corrected IP Rating values."""
    IP_55 = "IP-55"
    IP_56 = "IP-56"
    IP_66 = "IP-66"


class Pump(BaseModel):
    __tablename__ = 'pumps'
    
    pump_model = Column(String(120), nullable=False)
    
    # Duty Point Information (stored in base units: L/s and kPa)
    nominal_flow = Column(Float, nullable=True)
    nominal_head = Column(Float, nullable=True)

    inlet_size = Column(Float)
    outlet_size = Column(Float)
    rpm = Column(Integer)
    material = Column(String(120))
    ip_rating = Column(PyEnum(PumpIPRating), nullable=True)
    notes = Column(Text, nullable=True)
    manufacturer_url = Column(String(500), nullable=True)
    
    # Relationship to its assemblies
    assemblies = relationship("PumpAssembly", back_populates="pump", cascade="all, delete-orphan")


class InertiaBase(BaseModel):
    __tablename__ = 'inertia_bases'
    
    model = Column(String(120), unique=True, nullable=False)
    length = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)


class SeismicSpring(BaseModel):
    __tablename__ = 'seismic_springs'

    model = Column(String(120), unique=True, nullable=False)
    rated_load = Column(Integer)
    deflection = Column(Integer)
    
    # This relationship points back to the PumpAssembly model
    pump_assemblies = relationship("PumpAssembly", secondary='assembly_springs', back_populates="springs")


class RubberMount(BaseModel):
    __tablename__ = 'rubber_mounts'

    model = Column(String(120), unique=True, nullable=False)
    rated_load = Column(Integer)
    deflection = Column(Integer)