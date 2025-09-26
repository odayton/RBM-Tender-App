"""
Contact factory for generating test contacts
"""

import factory
from app.models.customers.customer_model import Contact
from app.models.customers.company_model import Company


class ContactFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test contacts."""
    
    class Meta:
        model = Contact
        sqlalchemy_session_persistence = 'flush'
    
    name = factory.Faker('name')
    email = factory.Sequence(lambda n: f'contact{n}@example.com')
    phone_number = factory.Faker('phone_number')
    mobile_number = factory.Faker('phone_number')
    position = factory.Faker('job')
    department = factory.Faker('word')
    is_primary = False
    is_active = True
    company = factory.SubFactory('tests.factories.company_factory.CompanyFactory')


class PrimaryContactFactory(ContactFactory):
    """Factory for creating primary contacts."""
    is_primary = True
