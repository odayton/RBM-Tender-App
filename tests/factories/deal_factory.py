"""
Deal factory for generating test deals
"""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyFloat, FuzzyInteger
from app.models import Deal, DealStage, DealType, AustralianState, User
from app.models.customers.company_model import Company
from app.models.customers.customer_model import Contact


class DealFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test deals."""
    
    class Meta:
        model = Deal
        sqlalchemy_session_persistence = 'flush'
    
    project_name = factory.Sequence(lambda n: f'Test Project {n}')
    deal_type = FuzzyChoice([DealType.HVAC, DealType.PLUMBING, DealType.HYDRONIC_HEATING])
    state = FuzzyChoice([AustralianState.NSW, AustralianState.VIC, AustralianState.QLD, AustralianState.WA])
    stage = FuzzyChoice([DealStage.SALES_LEAD, DealStage.PROPOSAL, DealStage.NEGOTIATION, DealStage.CLOSED_WON])
    total_amount = FuzzyFloat(10000.0, 100000.0)
    probability = FuzzyFloat(10.0, 90.0)
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True
    owner = factory.SubFactory('tests.factories.user_factory.UserFactory')
    
    @factory.post_generation
    def companies(obj, create, extracted, **kwargs):
        """Add companies to deal."""
        if extracted:
            for company in extracted:
                obj.companies.append(company)
        else:
            # Add a random company if none provided
            from tests.factories.company_factory import CompanyFactory
            company = CompanyFactory()
            obj.companies.append(company)
    
    @factory.post_generation
    def contacts(obj, create, extracted, **kwargs):
        """Add contacts to deal."""
        if extracted:
            for contact in extracted:
                obj.contacts.append(contact)
        else:
            # Add a random contact if none provided
            from tests.factories.contact_factory import ContactFactory
            contact = ContactFactory()
            obj.contacts.append(contact)


class HVACDealFactory(DealFactory):
    """Factory for creating HVAC deals."""
    deal_type = DealType.HVAC
    project_name = factory.Sequence(lambda n: f'HVAC Project {n}')


class PlumbingDealFactory(DealFactory):
    """Factory for creating plumbing deals."""
    deal_type = DealType.PLUMBING
    project_name = factory.Sequence(lambda n: f'Plumbing Project {n}')


class HydronicHeatingDealFactory(DealFactory):
    """Factory for creating hydronic heating deals."""
    deal_type = DealType.HYDRONIC_HEATING
    project_name = factory.Sequence(lambda n: f'Hydronic Heating Project {n}')


class ClosedWonDealFactory(DealFactory):
    """Factory for creating closed won deals."""
    stage = DealStage.CLOSED_WON
    probability = 100.0


class SalesLeadDealFactory(DealFactory):
    """Factory for creating sales lead deals."""
    stage = DealStage.SALES_LEAD
    probability = FuzzyFloat(10.0, 30.0)
