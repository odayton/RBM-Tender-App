from sqlalchemy import (
    Column, String, Integer, ForeignKey, Numeric, Float, Text, Enum as PyEnum
)
from sqlalchemy.orm import relationship
from ..base_model import BaseModel
from enum import Enum

# Note: The import for assembly_springs is removed from this file as it's no longer needed here.

class PumpIPRating(Enum):
    IP44 = "IP44"
    IP55 = "IP55"
    IP65 = "IP65"
    IP66 = "IP66"
    IP67 = "IP67"
    IP68 = "IP68"


class Pump(BaseModel):
    __tablename__ = 'pumps'
    
    pump_model = Column(String(120), nullable=False)
    inlet_size = Column(Float)
    outlet_size = Column(Float)
    rpm = Column(Integer)
    material = Column(String(120))
    ip_rating = Column(PyEnum(PumpIPRating), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationship to its assemblies. This still works.
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