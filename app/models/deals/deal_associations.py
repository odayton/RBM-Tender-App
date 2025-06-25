from sqlalchemy import Column, Integer, ForeignKey, Table
from ..base_model import BaseModel

# This table links Deals and Contacts (Many-to-Many)
deal_contacts = Table('deal_contacts', BaseModel.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('contact_id', Integer, ForeignKey('contacts.id'), primary_key=True)
)

# This table links Deals and Companies (Many-to-Many)
deal_companies = Table('deal_companies', BaseModel.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True)
)