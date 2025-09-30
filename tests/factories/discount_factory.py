"""
Discount Factory for generating test discount data
"""

from factory import Factory, Faker, Sequence
from app.models.deals.deal_models import Discount


class DiscountFactory(Factory):
    """Factory for creating test Discount instances."""
    
    class Meta:
        model = Discount
    
    code = Sequence(lambda n: f"TEST{n:03d}")
    percentage = Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=5, max_value=50)
    description = Faker('sentence', nb_words=4)
    is_active = True
    valid_from = Faker('date_time_between', start_date='-30d', end_date='now')
    valid_until = Faker('date_time_between', start_date='now', end_date='+30d')
