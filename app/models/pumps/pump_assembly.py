from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, JSON, Table
from sqlalchemy.orm import relationship, validates
from ..base_model import BaseModel
from app.core.core_errors import ValidationError
from .pump_model import Pump

assembly_springs = Table('assembly_springs', BaseModel.metadata,
    Column('assembly_id', Integer, ForeignKey('pump_assemblies.id'), primary_key=True),
    Column('spring_id', Integer, ForeignKey('springs.id'), primary_key=True),
    Column('quantity', Integer, default=1)
)

assembly_crossovers = Table('assembly_crossovers', BaseModel.metadata,
    Column('assembly_id', Integer, ForeignKey('pump_assemblies.id'), primary_key=True),
    Column('crossover_id', Integer, ForeignKey('crossovers.id'), primary_key=True)
)

class PumpAssembly(BaseModel):
    """Model for complete pump assemblies including all components"""
    __tablename__ = 'pump_assemblies'

    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False)
    assembly_number = Column(String(50), unique=True, nullable=False)
    inertia_base_id = Column(Integer, ForeignKey('inertia_bases.id'))
    total_list_price = Column(Numeric(10, 2))
    total_net_price = Column(Numeric(10, 2))
    configuration = Column(JSON)

    pump = relationship("Pump", backref="assemblies")
    inertia_base = relationship("InertiaBase")
    springs = relationship("Spring", secondary=assembly_springs)
    crossovers = relationship("Crossover", secondary=assembly_crossovers)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configuration = kwargs.get('configuration', {})

class InertiaBase(BaseModel):
    """Model for inertia bases"""
    __tablename__ = 'inertia_bases'

    part_number = Column(String(50), unique=True, nullable=False)
    size = Column(String(50), nullable=False)

    @validates('size')
    def validate_size(self, key, size):
        if not size or 'X' not in size:
            raise ValidationError("Size must be in format 'LENGTH X WIDTH X HEIGHT'")
        return size

class Spring(BaseModel):
    """Model for springs"""
    __tablename__ = 'springs'

    part_number = Column(String(50), unique=True, nullable=False)
    type = Column(String(50))

class Crossover(BaseModel):
    """Model for crossovers"""
    __tablename__ = 'crossovers'

    part_number = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))

class AssemblyMethods:
    """Mixin class for PumpAssembly methods"""
    
    def calculate_total_price(self) -> Dict[str, Decimal]:
        """
        Calculate total list and net prices for the assembly.
        NOTE: This logic needs to be re-implemented to fetch prices
        from the new pricing system (e.g., PriceList or ComponentPrice models).
        """
        # Example future logic:
        # price_list = PriceList.query.filter_by(is_active=True).first()
        # list_price = price_list.get_price('pump', self.pump_id).get('list_price')
        # ... etc.
        pass

    def update_prices(self) -> None:
        """Update the total prices of the assembly"""
        prices = self.calculate_total_price()
        if prices:
            self.total_list_price = prices.get('list_price')
            self.total_net_price = prices.get('net_price')

for method_name in dir(AssemblyMethods):
    if not method_name.startswith('_'):
        setattr(PumpAssembly, method_name, getattr(AssemblyMethods, method_name))