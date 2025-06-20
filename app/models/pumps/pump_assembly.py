from typing import Dict, Any
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship

from ..base_model import BaseModel
from .pump_associations import assembly_springs # Import from our new file

class PumpAssembly(BaseModel):
    """
    Model for a complete, configured pump assembly including all components.
    Inherits id, created_at, and updated_at from BaseModel.
    """
    __tablename__ = 'pump_assemblies'

    # --- Columns ---
    assembly_number = Column(String(50), unique=True, nullable=False, index=True)
    total_list_price = Column(Numeric(10, 2))
    total_net_price = Column(Numeric(10, 2))
    configuration = Column(JSON) # To store options like voltage, phase, etc.

    # --- Foreign Keys ---
    pump_id = Column(Integer, ForeignKey('pumps.id'), nullable=False)
    inertia_base_id = Column(Integer, ForeignKey('inertia_bases.id'))
    
    # --- Relationships ---
    pump = relationship("Pump", backref="assemblies")
    inertia_base = relationship("InertiaBase")
    
    # Many-to-many relationship for springs
    springs = relationship("SeismicSpring", secondary=assembly_springs)
    
    # Example for another many-to-many relationship
    # crossovers = relationship("Crossover", secondary=assembly_crossovers)

    def calculate_total_price(self) -> Dict[str, Decimal]:
        """
        Calculates the total list and net prices for the assembly.
        This method will fetch prices for each component from the pricing system.
        NOTE: This is placeholder logic and needs full implementation.
        """
        # Future logic will look something like this:
        # price_list = PriceList.get_active()
        # total_list = self.pump.get_price(price_list).get('list_price', 0)
        # total_list += self.inertia_base.get_price(price_list).get('list_price', 0)
        # for spring in self.springs:
        #     # Logic needs to account for quantity from the association table
        #     total_list += spring.get_price(price_list).get('list_price', 0)
        
        # For now, return a default
        return {
            'list_price': self.total_list_price or Decimal('0.0'),
            'net_price': self.total_net_price or Decimal('0.0')
        }

    def update_prices(self):
        """Updates the stored total prices by recalculating them."""
        prices = self.calculate_total_price()
        self.total_list_price = prices['list_price']
        self.total_net_price = prices['net_price']