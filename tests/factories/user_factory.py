"""
User factory for generating test users
"""

import factory
from factory.fuzzy import FuzzyChoice
from app.models import User, UserRole


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
        sqlalchemy_session_persistence = 'flush'
        sqlalchemy_session = None  # Will be set by fixture
    
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.Sequence(lambda n: f'testuser{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = factory.LazyFunction(lambda: '+61 2 1234 5678')  # Fixed length phone number
    role = FuzzyChoice([UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES, UserRole.VIEWER])
    is_active = True
    force_password_change = False
    password_hash = factory.LazyFunction(lambda: 'pbkdf2:sha256:600000$test$test')  # Set a default password hash
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        if extracted:
            obj.password = extracted  # Use the property setter
        else:
            obj.password = 'password123'  # Use the property setter


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""
    role = UserRole.ADMIN
    username = factory.Sequence(lambda n: f'admin{n}')
    email = factory.Sequence(lambda n: f'admin{n}@example.com')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        if extracted:
            obj.password = extracted  # Use the property setter
        else:
            obj.password = 'password123'  # Use the property setter


class SalesUserFactory(UserFactory):
    """Factory for creating sales users."""
    role = UserRole.SALES
    username = factory.Sequence(lambda n: f'sales{n}')
    email = factory.Sequence(lambda n: f'sales{n}@example.com')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        if extracted:
            obj.password = extracted  # Use the property setter
        else:
            obj.password = 'password123'  # Use the property setter


class ManagerUserFactory(UserFactory):
    """Factory for creating manager users."""
    role = UserRole.MANAGER
    username = factory.Sequence(lambda n: f'manager{n}')
    email = factory.Sequence(lambda n: f'manager{n}@example.com')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        if extracted:
            obj.password = extracted  # Use the property setter
        else:
            obj.password = 'password123'  # Use the property setter


class ViewerUserFactory(UserFactory):
    """Factory for creating viewer users."""
    role = UserRole.VIEWER
    username = factory.Sequence(lambda n: f'viewer{n}')
    email = factory.Sequence(lambda n: f'viewer{n}@example.com')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        if extracted:
            obj.password = extracted  # Use the property setter
        else:
            obj.password = 'password123'  # Use the property setter
