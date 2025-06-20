from sqlalchemy import Column, Integer, ForeignKey, Table
from ..base_model import BaseModel

# This table links the Deal and Contact models in a many-to-many relationship.
# It allows a single deal to be associated with multiple contacts, and a single
# contact to be associated with multiple deals.
deal_contacts = Table('deal_contacts', BaseModel.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('contact_id', Integer, ForeignKey('contacts.id'), primary_key=True)
)

# You can add other association tables here as needed, for example:
# deal_users = Table('deal_users', BaseModel.metadata,
#     Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
#     Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
# )