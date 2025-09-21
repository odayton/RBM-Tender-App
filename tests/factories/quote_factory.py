"""
Quote factory for generating test quotes
"""

import factory
from factory.fuzzy import FuzzyFloat, FuzzyInteger
from app.models.deals.deal_models import Quote, QuoteRecipient, QuoteOption, QuoteLineItem
from app.models.customers.company_model import Company
from app.models.products.product_model import Product


class QuoteRecipientFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating quote recipients."""
    
    class Meta:
        model = QuoteRecipient
        sqlalchemy_session_persistence = 'flush'
    
    contact_person = factory.Faker('name')
    delivery_method = factory.Faker('random_element', elements=['email', 'post', 'fax'])
    company = factory.SubFactory('tests.factories.company_factory.CompanyFactory')


class QuoteOptionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating quote options."""
    
    class Meta:
        model = QuoteOption
        sqlalchemy_session_persistence = 'flush'
    
    name = factory.Sequence(lambda n: f'Option {n}')
    freight_charge = FuzzyFloat(50.0, 500.0)


class QuoteLineItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating quote line items."""
    
    class Meta:
        model = QuoteLineItem
        sqlalchemy_session_persistence = 'flush'
    
    quantity = FuzzyInteger(1, 10)
    unit_price = FuzzyFloat(100.0, 2000.0)
    notes = factory.Faker('text', max_nb_chars=50)
    product = factory.SubFactory('tests.factories.product_factory.ProductFactory')


class QuoteFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test quotes."""
    
    class Meta:
        model = Quote
        sqlalchemy_session_persistence = 'flush'
    
    revision = FuzzyInteger(1, 5)
    notes = factory.Faker('text', max_nb_chars=100)
    recipient = factory.SubFactory(QuoteRecipientFactory)
    
    @factory.post_generation
    def options(obj, create, extracted, **kwargs):
        """Add options to quote."""
        if extracted:
            for option in extracted:
                obj.options.append(option)
        else:
            # Add a default option if none provided
            option = QuoteOptionFactory()
            obj.options.append(option)
            
            # Add a line item to the option
            line_item = QuoteLineItemFactory(option=option)
            obj.options[0].line_items.append(line_item)


class MultiOptionQuoteFactory(QuoteFactory):
    """Factory for creating quotes with multiple options."""
    
    @factory.post_generation
    def options(obj, create, extracted, **kwargs):
        """Add multiple options to quote."""
        if extracted:
            for option in extracted:
                obj.options.append(option)
        else:
            # Add 3 options with line items
            for i in range(3):
                option = QuoteOptionFactory(name=f'Option {i+1}')
                obj.options.append(option)
                
                # Add 2-3 line items per option
                for j in range(2):
                    line_item = QuoteLineItemFactory(option=option)
                    obj.options[i].line_items.append(line_item)


class SimpleQuoteFactory(QuoteFactory):
    """Factory for creating simple quotes with one option and one line item."""
    
    @factory.post_generation
    def options(obj, create, extracted, **kwargs):
        """Add single option to quote."""
        if extracted:
            for option in extracted:
                obj.options.append(option)
        else:
            # Add one option with one line item
            option = QuoteOptionFactory(name='Standard Package')
            obj.options.append(option)
            
            line_item = QuoteLineItemFactory(option=option)
            obj.options[0].line_items.append(line_item)
