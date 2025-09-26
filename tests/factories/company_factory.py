"""
Company factory for generating test companies
"""

import factory
from app.models.customers.company_model import Company


class CompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test companies."""
    
    class Meta:
        model = Company
        sqlalchemy_session_persistence = 'flush'
    
    company_name = factory.Sequence(lambda n: f'Test Company {n} Pty Ltd')
    phone_number = factory.Faker('phone_number')
    domain = factory.LazyAttribute(lambda obj: f'{obj.company_name.lower().replace(" ", "").replace(".", "")}.com')
