"""
Pytest configuration and fixtures for RBM Tender App tests
"""

import os
import sys
import pytest
import tempfile
from datetime import datetime
from flask import Flask

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.core.core_config import TestingConfig
from app.extensions import db, login_manager
from app.models import User, UserRole, Deal, DealStage, DealType, AustralianState
from app.models.customers.company_model import Company
from app.models.customers.customer_model import Contact
from app.models.products.product_model import Product
from app.models.deals.deal_models import Quote, QuoteRecipient, QuoteOption, QuoteLineItem


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Configure test app with PostgreSQL
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        db.create_all()
        
        # Set the session for all factories
        from tests.factories import UserFactory, CompanyFactory, ContactFactory, DealFactory, ProductFactory, QuoteFactory
        UserFactory._meta.sqlalchemy_session = db.session
        CompanyFactory._meta.sqlalchemy_session = db.session
        ContactFactory._meta.sqlalchemy_session = db.session
        DealFactory._meta.sqlalchemy_session = db.session
        ProductFactory._meta.sqlalchemy_session = db.session
        QuoteFactory._meta.sqlalchemy_session = db.session
        
        # Also set session for subclasses
        from tests.factories.user_factory import AdminUserFactory, SalesUserFactory, ManagerUserFactory, ViewerUserFactory
        AdminUserFactory._meta.sqlalchemy_session = db.session
        SalesUserFactory._meta.sqlalchemy_session = db.session
        ManagerUserFactory._meta.sqlalchemy_session = db.session
        ViewerUserFactory._meta.sqlalchemy_session = db.session
        
        # Start a transaction that will be rolled back
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.configure(bind=connection)
        
        yield db.session
        
        # Rollback the transaction to clean up
        transaction.rollback()
        connection.close()
        db.session.remove()


@pytest.fixture(scope='function')
def auth_headers(client, admin_user):
    """Create authentication headers for API testing."""
    # Login and get session
    response = client.post('/auth/login', data={
        'email': admin_user.email,
        'password': 'password123'
    }, follow_redirects=True)
    
    # Return headers for authenticated requests
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'test-token'  # For testing purposes
    }


@pytest.fixture(scope='function')
def admin_user(db_session):
    """Create admin user for testing."""
    user = User(
        username='admin_test',
        email='admin@test.com',
        first_name='Admin',
        last_name='Test',
        role=UserRole.ADMIN,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def sales_user(db_session):
    """Create sales user for testing."""
    user = User(
        username='sales_test',
        email='sales@test.com',
        first_name='Sales',
        last_name='Test',
        role=UserRole.SALES,
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_company(db_session):
    """Create test company."""
    company = Company(
        company_name='Test Company Pty Ltd',
        address='123 Test Street, Test City, TC 1234',
        phone_number='+61 2 1234 5678',
        website='https://testcompany.com',
        abn='12345678901'
    )
    db_session.add(company)
    db_session.commit()
    return company


@pytest.fixture(scope='function')
def test_contact(db_session, test_company):
    """Create test contact."""
    contact = Contact(
        name='John Test',
        email='john@testcompany.com',
        phone_number='+61 2 1234 5679',
        position='Project Manager',
        company_id=test_company.id,
        is_primary=True
    )
    db_session.add(contact)
    db_session.commit()
    return contact


@pytest.fixture(scope='function')
def test_deal(db_session, admin_user, test_company, test_contact):
    """Create test deal."""
    deal = Deal(
        project_name='Test HVAC Project',
        deal_type=DealType.HVAC,
        state=AustralianState.NSW,
        stage=DealStage.SALES_LEAD,
        owner_id=admin_user.id,
        total_amount=50000.00,
        probability=75.0
    )
    deal.companies.append(test_company)
    deal.contacts.append(test_contact)
    db_session.add(deal)
    db_session.commit()
    return deal


@pytest.fixture(scope='function')
def test_product(db_session):
    """Create test product."""
    product = Product(
        sku='TEST-001',
        name='Test HVAC Unit',
        description='A test HVAC unit for testing purposes',
        unit_price=1500.00,
        category='HVAC',
        brand='TestBrand',
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture(scope='function')
def test_quote(db_session, test_deal, test_company):
    """Create test quote."""
    # Create quote recipient
    recipient = QuoteRecipient(
        deal_id=test_deal.id,
        company_id=test_company.id,
        contact_person='John Test',
        delivery_method='email'
    )
    db_session.add(recipient)
    db_session.flush()
    
    # Create quote
    quote = Quote(
        recipient_id=recipient.id,
        revision=1,
        notes='Test quote for testing purposes'
    )
    db_session.add(quote)
    db_session.flush()
    
    # Create quote option
    option = QuoteOption(
        quote_id=quote.id,
        name='Standard Package',
        freight_charge=150.00
    )
    db_session.add(option)
    db_session.flush()
    
    # Create line item
    line_item = QuoteLineItem(
        option_id=option.id,
        product_id=test_product(db_session).id,
        quantity=2,
        unit_price=1500.00,
        notes='Test line item'
    )
    db_session.add(line_item)
    db_session.commit()
    
    return quote


@pytest.fixture(scope='function')
def logged_in_client(client, admin_user):
    """Create logged-in client for testing."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    
    return client


# Performance testing fixtures
@pytest.fixture(scope='function')
def performance_data(db_session, admin_user):
    """Create performance test data."""
    # Create multiple deals for performance testing
    deals = []
    for i in range(10):
        deal = Deal(
            project_name=f'Performance Test Deal {i}',
            deal_type=DealType.HVAC,
            state=AustralianState.NSW,
            stage=DealStage.SALES_LEAD,
            owner_id=admin_user.id,
            total_amount=10000.00 + (i * 1000),
            probability=50.0 + (i * 5)
        )
        db_session.add(deal)
        deals.append(deal)
    
    db_session.commit()
    return deals


# Security testing fixtures
@pytest.fixture(scope='function')
def malicious_inputs():
    """Provide malicious inputs for security testing."""
    return {
        'sql_injection': "'; DROP TABLE users; --",
        'xss': '<script>alert("XSS")</script>',
        'path_traversal': '../../../etc/passwd',
        'command_injection': '; rm -rf /',
        'ldap_injection': '*)(uid=*))(|(uid=*'
    }


# Mock fixtures for external services
@pytest.fixture(scope='function')
def mock_sentry():
    """Mock Sentry for testing."""
    import pytest
    with pytest.MonkeyPatch().context() as m:
        m.setattr('app.core.core_sentry.sentry_sdk', None)
        yield m


@pytest.fixture(scope='function')
def mock_redis():
    """Mock Redis for testing."""
    import pytest
    with pytest.MonkeyPatch().context() as m:
        m.setattr('app.core.core_cache.cache_manager', None)
        yield m


# Test utilities
def assert_response_success(response):
    """Assert that response is successful."""
    assert response.status_code in [200, 201, 302]


def assert_response_error(response, expected_status=400):
    """Assert that response is an error."""
    assert response.status_code == expected_status


def assert_json_response(response, expected_keys=None):
    """Assert that response is valid JSON with expected keys."""
    assert response.content_type == 'application/json'
    data = response.get_json()
    assert data is not None
    if expected_keys:
        for key in expected_keys:
            assert key in data
    return data


def assert_html_response(response, expected_text=None):
    """Assert that response is HTML with expected text."""
    assert 'text/html' in response.content_type
    if expected_text:
        assert expected_text.encode() in response.data
    return response.data


# Test data generators
def generate_test_email():
    """Generate unique test email."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'test{timestamp}@example.com'


def generate_test_username():
    """Generate unique test username."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'testuser{timestamp}'


def generate_test_company_name():
    """Generate unique test company name."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'Test Company {timestamp} Pty Ltd'
