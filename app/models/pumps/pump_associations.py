from sqlalchemy import Column, Integer, ForeignKey, Table
from ..base_model import BaseModel

# This table links PumpAssembly to the SeismicSprings used in it.
# It includes a 'quantity' column to specify how many of each spring are needed.
assembly_springs = Table('assembly_springs', BaseModel.metadata,
    Column('assembly_id', Integer, ForeignKey('pump_assemblies.id'), primary_key=True),
    Column('spring_id', Integer, ForeignKey('seismic_springs.id'), primary_key=True),
    Column('quantity', Integer, default=1, nullable=False)
)

# This table could be used for crossovers or other many-to-many components.
# We will define it here for structural consistency.
# assembly_crossovers = Table('assembly_crossovers', BaseModel.metadata,
#     Column('assembly_id', Integer, ForeignKey('pump_assemblies.id'), primary_key=True),
#     Column('crossover_id', Integer, ForeignKey('crossovers.id'), primary_key=True)
# )