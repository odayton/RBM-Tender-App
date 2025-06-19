from sqlalchemy import Column, Integer, ForeignKey, Table
from ..base_model import BaseModel

# This table links the Deal and Customer models in a many-to-many relationship.
deal_customers = Table('deal_customers', BaseModel.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('customer_id', Integer, ForeignKey('customers.id'), primary_key=True)
)