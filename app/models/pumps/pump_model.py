from typing import List
from sqlalchemy import (Column, String, Float, Integer, ForeignKey,
                        Enum, Text, Numeric, Table)
from sqlalchemy.orm import relationship, backref

from ..base_model import BaseModel
from ...core.core_errors import ValidationError
import enum

# =================================================================
# ENUMS
# =================================================================

class PumpSeries(enum.Enum):
    """Enum for different pump series for type safety and consistency."""
    NBG = "NBG"
    CR = "CR"
    TP = "TP"
    CM = "CM"
    MAGNA = "MAGNA"
    UPS = "UPS"
    CRE = "CRE"
    TPE = "TPE"
    NK = "NK"

# =================================================================
# PUMP AND COMPONENT MODELS
# =================================================================

class Pump(BaseModel):
    """
    The core Pump model.
    """
    __tablename__ = 'pumps'

    part_number = Column(String(50), unique=True, nullable=False, index=True)
    series = Column(Enum(PumpSeries), nullable=False)
    frame_size = Column(String(50))
    poles = Column(Integer)
    power_kw = Column(Float)
    
    flow_rate = Column(Float)
    head = Column(Float)
    efficiency = Column(Float)
    
    assemblies = relationship("PumpAssembly", back_populates="pump")
    ip_ratings = relationship("PumpIPRating", back_populates="pump", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Pump(part_number='{self.part_number}')>"

class InertiaBase(BaseModel):
    """Model for pump inertia bases."""
    __tablename__ = 'inertia_bases'

    part_number = Column(String(50), unique=True, nullable=False, index=True)
    dimensions = Column(String(100))
    weight_kg = Column(Numeric(10, 2))
    
    assemblies = relationship("PumpAssembly", back_populates="inertia_base")

    def __repr__(self) -> str:
        return f"<InertiaBase(part_number='{self.part_number}')>"

class SeismicSpring(BaseModel):
    """Model for seismic springs."""
    __tablename__ = 'seismic_springs'

    part_number = Column(String(50), unique=True, nullable=False, index=True)
    spring_rate_k = Column(Float)
    max_deflection_mm = Column(Float)
    
    assemblies = relationship("AssemblySpringAssociation", back_populates="spring", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SeismicSpring(part_number='{self.part_number}')>"

# --- ADD THIS NEW MODEL ---
class RubberMount(BaseModel):
    """Model for rubber mounts."""
    __tablename__ = 'rubber_mounts'

    part_number = Column(String(50), unique=True, nullable=False, index=True)
    mount_type = Column(String(100))
    load_capacity_kg = Column(Numeric(10, 2))

    def __repr__(self) -> str:
        return f"<RubberMount(part_number='{self.part_number}')>"
# --- END OF ADDITION ---

class PumpIPRating(BaseModel):
    """Model for pump IP ratings."""
    __tablename__ = 'pump_ip_ratings'
    
    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False)
    rating = Column(String(10), nullable=False)
    
    pump = relationship("Pump", back_populates="ip_ratings")

    def __repr__(self) -> str:
        return f"<PumpIPRating(pump_id={self.pump_id}, rating='{self.rating}')>"


# =================================================================
# ASSEMBLY & ASSOCIATION MODELS
# =================================================================

class PumpAssembly(BaseModel):
    """
    A complete, configured pump assembly.
    """
    __tablename__ = 'pump_assemblies'

    assembly_number = Column(String(50), unique=True, nullable=False, index=True)

    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False)
    inertia_base_id = Column(Integer, ForeignKey('inertia_bases.id'))
    
    pump = relationship("Pump", back_populates="assemblies")
    inertia_base = relationship("InertiaBase", back_populates="assemblies")
    
    springs = relationship("AssemblySpringAssociation", back_populates="assembly", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PumpAssembly(assembly_number='{self.assembly_number}')>"


class AssemblySpringAssociation(BaseModel):
    """
    Association Object for the PumpAssembly -> SeismicSpring relationship.
    """
    __tablename__ = 'assembly_springs'

    assembly_id = Column(Integer, ForeignKey('pump_assemblies.id'), primary_key=True)
    spring_id = Column(Integer, ForeignKey('seismic_springs.id'), primary_key=True)
    quantity = Column(Integer, default=1, nullable=False)

    assembly = relationship("PumpAssembly", back_populates="springs")
    spring = relationship("SeismicSpring", back_populates="assemblies")