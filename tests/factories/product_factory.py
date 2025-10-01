"""
Product factory for generating test products
"""

import factory
from factory.fuzzy import FuzzyFloat, FuzzyInteger
from app.models.products.product_model import Product


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test products."""
    
    class Meta:
        model = Product
        sqlalchemy_session_persistence = 'flush'
    
    # New 14-column schema
    category = factory.Faker('word')
    sub_category = factory.Faker('word')
    series = factory.Sequence(lambda n: f'SERIES-{n}')
    item_no = factory.Sequence(lambda n: f'ITEM-{n:03d}')
    description = factory.Sequence(lambda n: f'Test Product {n}')
    pack = factory.Faker('word')
    carton_qty = FuzzyInteger(1, 10)
    list_price = FuzzyFloat(100.0, 5000.0)
    discount_code = None
    notes = factory.Faker('text', max_nb_chars=100)
    weight_kg = FuzzyFloat(1.0, 100.0)
    dimensions = factory.LazyAttribute(lambda obj: f'{obj.weight_kg * 10:.0f}x{obj.weight_kg * 5:.0f}x{obj.weight_kg * 2:.0f}cm')
    lead_time_days = FuzzyInteger(1, 30)
    is_active = True


class HVACProductFactory(ProductFactory):
    """Factory for creating HVAC products."""
    category = 'HVAC'
    sub_category = 'Units'
    description = factory.Sequence(lambda n: f'HVAC Unit {n}')
    item_no = factory.Sequence(lambda n: f'HVAC-{n:03d}')


class PlumbingProductFactory(ProductFactory):
    """Factory for creating plumbing products."""
    category = 'Plumbing'
    sub_category = 'Fixtures'
    description = factory.Sequence(lambda n: f'Plumbing Fixture {n}')
    item_no = factory.Sequence(lambda n: f'PLUMB-{n:03d}')


class HydronicProductFactory(ProductFactory):
    """Factory for creating hydronic heating products."""
    category = 'Hydronic Heating'
    sub_category = 'Components'
    description = factory.Sequence(lambda n: f'Hydronic Component {n}')
    item_no = factory.Sequence(lambda n: f'HYDRO-{n:03d}')
