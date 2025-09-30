"""
Schema Compatibility Tests

These tests validate that the model definitions match the actual database schema.
They catch issues like missing columns that cause 500 errors in production.
"""

import pytest
from sqlalchemy import inspect, text
from app.models.products.product_model import Product
from app.models.deals.deal_models import Deal, Quote, QuoteLineItem
from app.models.customers.company_model import Company
from app.models.customers.customer_model import Contact
from app.models.user_model import User


class TestSchemaCompatibility:
    """Test that model schemas match database schema."""
    
    def test_product_model_schema_compatibility(self, db_session):
        """Test that Product model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if products table exists
        assert inspector.has_table('products'), "Products table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('products')]
        
        # Define expected columns based on current model
        expected_columns = [
            'sku', 'name', 'unit_price', 'category', 'sub_category',
            'series', 'item_no', 'description', 'discount_code',
            'notes', 'weight_kg', 'dimensions', 'lead_time_days',
            'is_active', 'brand', 'model_number', 'stock_quantity',
            'reorder_level', 'id', 'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in products table: {missing_columns}"
        
        # Check for unexpected columns (warn but don't fail)
        unexpected_columns = set(actual_columns) - set(expected_columns)
        if unexpected_columns:
            print(f"Warning: Unexpected columns in products table: {unexpected_columns}")
    
    def test_deal_model_schema_compatibility(self, db_session):
        """Test that Deal model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if deals table exists
        assert inspector.has_table('deals'), "Deals table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('deals')]
        
        # Define expected columns based on current model
        expected_columns = [
            'id', 'name', 'stage', 'type', 'amount', 'location',
            'close_date', 'owner', 'contact_id', 'company_id',
            'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in deals table: {missing_columns}"
    
    def test_quote_model_schema_compatibility(self, db_session):
        """Test that Quote model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if quotes table exists
        assert inspector.has_table('quotes'), "Quotes table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('quotes')]
        
        # Define expected columns based on current model
        expected_columns = [
            'id', 'deal_id', 'name', 'status', 'total_amount',
            'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in quotes table: {missing_columns}"
    
    def test_quote_line_item_model_schema_compatibility(self, db_session):
        """Test that QuoteLineItem model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if quote_line_items table exists
        assert inspector.has_table('quote_line_items'), "Quote line items table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('quote_line_items')]
        
        # Define expected columns based on current model
        expected_columns = [
            'id', 'quote_id', 'product_id', 'quantity', 'unit_price',
            'total_price', 'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in quote_line_items table: {missing_columns}"
    
    def test_company_model_schema_compatibility(self, db_session):
        """Test that Company model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if companies table exists
        assert inspector.has_table('companies'), "Companies table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('companies')]
        
        # Define expected columns based on current model
        expected_columns = [
            'id', 'company_name', 'contact_person', 'email',
            'phone', 'address', 'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in companies table: {missing_columns}"
    
    def test_contact_model_schema_compatibility(self, db_session):
        """Test that Contact model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if contacts table exists
        assert inspector.has_table('contacts'), "Contacts table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('contacts')]
        
        # Define expected columns based on current model
        expected_columns = [
            'id', 'company_id', 'representative_name', 'email',
            'phone', 'position', 'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in contacts table: {missing_columns}"
    
    def test_user_model_schema_compatibility(self, db_session):
        """Test that User model matches database schema."""
        inspector = inspect(db_session.bind)
        
        # Check if users table exists
        assert inspector.has_table('users'), "Users table does not exist"
        
        # Get actual columns from database
        actual_columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Define expected columns based on current model
        expected_columns = [
            'id', 'email', 'password_hash', 'first_name', 'last_name',
            'role', 'is_active', 'created_at', 'updated_at'
        ]
        
        # Check for missing columns
        missing_columns = set(expected_columns) - set(actual_columns)
        assert not missing_columns, f"Missing columns in users table: {missing_columns}"


class TestModelMethodsFunctionality:
    """Test that model methods work correctly with current schema."""
    
    def test_product_model_methods_work(self, db_session):
        """Test that Product model methods work with current schema."""
        from tests.factories import ProductFactory
        
        # Create a test product
        product = ProductFactory()
        db_session.add(product)
        db_session.commit()
        
        # Test methods that were failing before
        assert product.get_discounted_price() is not None
        assert product.get_list_price() is not None
        assert product.get_effective_price() is not None
        assert isinstance(product.is_low_stock(), bool)
        assert isinstance(product.is_out_of_stock(), bool)
        assert isinstance(product.get_availability_status(), str)
        assert isinstance(product.to_dict(), dict)
    
    def test_product_model_queries_work(self, db_session):
        """Test that Product model queries work with current schema."""
        from tests.factories import ProductFactory
        
        # Create test products
        product1 = ProductFactory(category='HVAC', unit_price=100.00)
        product2 = ProductFactory(category='Plumbing', unit_price=200.00)
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Test various queries that are used in routes
        products = Product.query.filter(Product.is_active == True).all()
        assert len(products) >= 2
        
        products = Product.query.filter(Product.category == 'HVAC').all()
        assert len(products) >= 1
        
        products = Product.query.filter(Product.unit_price <= 150.00).all()
        assert len(products) >= 1
        
        products = Product.query.filter(Product.name.ilike('%test%')).all()
        assert len(products) >= 2
    
    def test_deal_model_methods_work(self, db_session):
        """Test that Deal model methods work with current schema."""
        from tests.factories import DealFactory
        
        # Create a test deal
        deal = DealFactory()
        db_session.add(deal)
        db_session.commit()
        
        # Test basic methods
        assert isinstance(deal.to_dict(), dict)
        assert deal.name is not None
    
    def test_company_model_methods_work(self, db_session):
        """Test that Company model methods work with current schema."""
        from tests.factories import CompanyFactory
        
        # Create a test company
        company = CompanyFactory()
        db_session.add(company)
        db_session.commit()
        
        # Test basic methods
        assert isinstance(company.to_dict(), dict)
        assert company.company_name is not None


class TestDatabaseConstraints:
    """Test that database constraints are properly defined."""
    
    def test_product_constraints_exist(self, db_session):
        """Test that Product table constraints exist."""
        inspector = inspect(db_session.bind)
        
        # Get constraints for products table
        constraints = inspector.get_check_constraints('products')
        constraint_names = [c['name'] for c in constraints]
        
        # Check for important constraints
        expected_constraints = [
            'check_product_unit_price',
            'check_product_stock_quantity',
            'check_product_reorder_level',
            'check_product_lead_time'
        ]
        
        for constraint_name in expected_constraints:
            assert constraint_name in constraint_names, f"Missing constraint: {constraint_name}"
    
    def test_product_constraints_work(self, db_session):
        """Test that Product constraints actually work."""
        from tests.factories import ProductFactory
        
        # Test negative unit price constraint
        product = ProductFactory()
        product.unit_price = -100.00
        
        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.add(product)
            db_session.commit()
        
        db_session.rollback()
        
        # Test negative stock quantity constraint
        product = ProductFactory()
        product.stock_quantity = -10
        
        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.add(product)
            db_session.commit()
        
        db_session.rollback()


class TestForeignKeyIntegrity:
    """Test that foreign key relationships are intact."""
    
    def test_product_foreign_keys_work(self, db_session):
        """Test that Product foreign keys work correctly."""
        from tests.factories import ProductFactory, DiscountFactory
        
        # Create a discount
        discount = DiscountFactory()
        db_session.add(discount)
        db_session.flush()
        
        # Create a product with the discount
        product = ProductFactory()
        product.discount_code = discount.code
        db_session.add(product)
        db_session.commit()
        
        # Test that the relationship works
        assert product.discount is not None
        assert product.discount.code == discount.code
    
    def test_deal_foreign_keys_work(self, db_session):
        """Test that Deal foreign keys work correctly."""
        from tests.factories import DealFactory, CompanyFactory, ContactFactory
        
        # Create company and contact
        company = CompanyFactory()
        contact = ContactFactory()
        db_session.add_all([company, contact])
        db_session.flush()
        
        # Create a deal with the company and contact
        deal = DealFactory()
        deal.company_id = company.id
        deal.contact_id = contact.id
        db_session.add(deal)
        db_session.commit()
        
        # Test that the relationships work
        assert deal.company is not None
        assert deal.contact is not None
        assert deal.company.id == company.id
        assert deal.contact.id == contact.id


class TestSchemaMigrationCompatibility:
    """Test that schema changes don't break existing functionality."""
    
    def test_old_column_references_removed(self, db_session):
        """Test that old column references have been removed."""
        inspector = inspect(db_session.bind)
        
        # Get actual columns from products table
        actual_columns = [col['name'] for col in inspector.get_columns('products')]
        
        # These columns should NOT exist (they were removed)
        removed_columns = ['pack', 'carton_qty', 'list_price']
        
        for column in removed_columns:
            assert column not in actual_columns, f"Old column '{column}' still exists in database"
    
    def test_model_methods_use_correct_columns(self, db_session):
        """Test that model methods use the correct columns."""
        from tests.factories import ProductFactory
        
        # Create a test product
        product = ProductFactory()
        db_session.add(product)
        db_session.commit()
        
        # Test that get_list_price() uses unit_price (not the removed list_price)
        list_price = product.get_list_price()
        assert list_price == product.unit_price, "get_list_price() should use unit_price"
        
        # Test that the product can be serialized without errors
        product_dict = product.to_dict()
        assert 'unit_price' in product_dict
        assert 'list_price' not in product_dict  # Should not reference removed column
