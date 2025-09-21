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
    
    sku = factory.Sequence(lambda n: f'TEST-{n:03d}')
    name = factory.Sequence(lambda n: f'Test Product {n}')
    description = factory.Faker('text', max_nb_chars=100)
    unit_price = FuzzyFloat(100.0, 5000.0)
    category = factory.Faker('word')
    brand = factory.Faker('company')
    model_number = factory.Sequence(lambda n: f'MODEL-{n}')
    weight_kg = FuzzyFloat(1.0, 100.0)
    dimensions = factory.LazyAttribute(lambda obj: f'{obj.weight_kg * 10:.0f}x{obj.weight_kg * 5:.0f}x{obj.weight_kg * 2:.0f}cm')
    is_active = True
    stock_quantity = FuzzyInteger(0, 100)
    reorder_level = FuzzyInteger(5, 20)
    lead_time_days = FuzzyInteger(1, 30)


class HVACProductFactory(ProductFactory):
    """Factory for creating HVAC products."""
    category = 'HVAC'
    name = factory.Sequence(lambda n: f'HVAC Unit {n}')
    sku = factory.Sequence(lambda n: f'HVAC-{n:03d}')


class PlumbingProductFactory(ProductFactory):
    """Factory for creating plumbing products."""
    category = 'Plumbing'
    name = factory.Sequence(lambda n: f'Plumbing Fixture {n}')
    sku = factory.Sequence(lambda n: f'PLUMB-{n:03d}')


class HydronicProductFactory(ProductFactory):
    """Factory for creating hydronic heating products."""
    category = 'Hydronic Heating'
    name = factory.Sequence(lambda n: f'Hydronic Component {n}')
    sku = factory.Sequence(lambda n: f'HYDRO-{n:03d}')


class LowStockProductFactory(ProductFactory):
    """Factory for creating low stock products."""
    stock_quantity = factory.LazyAttribute(lambda obj: obj.reorder_level - 1)


class OutOfStockProductFactory(ProductFactory):
    """Factory for creating out of stock products."""
    stock_quantity = 0
