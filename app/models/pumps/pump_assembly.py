from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from ..base_model import BaseModel
from .pump_associations import assembly_springs
from .pump_model import SeismicSpring, Pump, InertiaBase, RubberMount


class PumpAssembly(BaseModel):
    """
    Represents a pre-defined assembly of a pump with its accessories.
    """
    __tablename__ = 'pump_assemblies'

    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False)
    inertia_base_id = Column(Integer, ForeignKey('inertia_bases.id'))
    rubber_mount_id = Column(Integer, ForeignKey('rubber_mounts.id'))
    
    # A friendly name for the assembly for easy identification
    assembly_name = Column(String(120), nullable=True, unique=True)

    # Relationships
    pump = relationship("Pump", back_populates="assemblies")
    inertia_base = relationship("InertiaBase")
    rubber_mount = relationship("RubberMount")
    
    # Many-to-Many relationship with SeismicSpring
    springs = relationship("SeismicSpring", secondary=assembly_springs, back_populates="pump_assemblies")
    
    # One-to-one relationship to the Product that represents this assembly
    product = relationship("Product", back_populates="pump_assembly", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PumpAssembly(id={self.id}, name='{self.assembly_name}')>"