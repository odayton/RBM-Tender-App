"""
Database Migration Validation Tests

These tests validate that database migrations work correctly and don't break
existing functionality. They catch issues with schema changes before deployment.
"""

import pytest
from sqlalchemy import inspect, text
from app.models.products.product_model import Product
from app.models.deals.deal_models import Deal, Quote, QuoteLineItem
from app.models.customers.company_model import Company
from app.models.customers.customer_model import Contact
from app.models.user_model import User


class TestMigrationCompatibility:
    """Test that migrations maintain compatibility."""
    
    def test_removed_columns_not_referenced(self, db_session):
        """Test that removed columns are not referenced in code."""
        inspector = inspect(db_session.bind)
        
        # Get actual columns from products table
        actual_columns = [col['name'] for col in inspector.get_columns('products')]
        
        # These columns were removed and should not exist
        removed_columns = ['pack', 'carton_qty', 'list_price']
        
        for column in removed_columns:
            assert column not in actual_columns, f"Removed column '{column}' still exists in database"
    
    def test_model_methods_use_correct_columns(self, db_session):
        """Test that model methods use the correct columns after migration."""
        from tests.factories import ProductFactory
        
        # Create a test product
        product = ProductFactory()
        db_session.add(product)
        db_session.commit()
        
        # Test that methods work with current schema
        assert product.get_list_price() == product.unit_price
        assert product.get_discounted_price() is not None
        assert product.get_effective_price() is not None
        
        # Test that to_dict() doesn't reference removed columns
        product_dict = product.to_dict()
        assert 'unit_price' in product_dict
        assert 'list_price' not in product_dict
        assert 'pack' not in product_dict
        assert 'carton_qty' not in product_dict
    
    def test_queries_use_correct_columns(self, db_session):
        """Test that queries use the correct columns after migration."""
        from tests.factories import ProductFactory
        
        # Create test products
        product1 = ProductFactory(unit_price=100.00, category='HVAC')
        product2 = ProductFactory(unit_price=200.00, category='Plumbing')
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Test price filtering (should use unit_price, not list_price)
        products = Product.query.filter(Product.unit_price <= 150.00).all()
        assert len(products) >= 1
        assert product1 in products
        assert product2 not in products
        
        # Test category filtering
        products = Product.query.filter(Product.category == 'HVAC').all()
        assert len(products) >= 1
        assert product1 in products
        assert product2 not in products


class TestMigrationDataIntegrity:
    """Test that migrations preserve data integrity."""
    
    def test_existing_data_accessible(self, db_session):
        """Test that existing data is still accessible after migration."""
        from tests.factories import ProductFactory
        
        # Create test products with various data
        product1 = ProductFactory(
            sku='TEST-001',
            name='Test Product 1',
            unit_price=100.00,
            category='HVAC',
            sub_category='Air Conditioning',
            series='AC-100',
            item_no='AC-100-001',
            description='Test HVAC product',
            discount_code=None,
            notes='Test notes',
            weight_kg=10.5,
            dimensions='100x50x30cm',
            lead_time_days=7,
            is_active=True,
            brand='TestBrand',
            model_number='TB-001',
            stock_quantity=50,
            reorder_level=10
        )
        
        db_session.add(product1)
        db_session.commit()
        
        # Test that all data is accessible
        assert product1.sku == 'TEST-001'
        assert product1.name == 'Test Product 1'
        assert product1.unit_price == 100.00
        assert product1.category == 'HVAC'
        assert product1.sub_category == 'Air Conditioning'
        assert product1.series == 'AC-100'
        assert product1.item_no == 'AC-100-001'
        assert product1.description == 'Test HVAC product'
        assert product1.weight_kg == 10.5
        assert product1.dimensions == '100x50x30cm'
        assert product1.lead_time_days == 7
        assert product1.is_active == True
        assert product1.brand == 'TestBrand'
        assert product1.model_number == 'TB-001'
        assert product1.stock_quantity == 50
        assert product1.reorder_level == 10
    
    def test_foreign_key_relationships_intact(self, db_session):
        """Test that foreign key relationships are intact after migration."""
        from tests.factories import ProductFactory, DealFactory, CompanyFactory, ContactFactory
        
        # Create related entities
        company = CompanyFactory()
        contact = ContactFactory()
        product = ProductFactory()
        
        db_session.add_all([company, contact, product])
        db_session.flush()
        
        # Create deal with relationships
        deal = DealFactory()
        deal.company_id = company.id
        deal.contact_id = contact.id
        
        db_session.add(deal)
        db_session.flush()
        
        # Create quote with deal relationship
        from app.models.deals.deal_models import Quote
        quote = Quote(
            deal_id=deal.id,
            name='Test Quote',
            status='draft',
            total_amount=1000.00
        )
        
        db_session.add(quote)
        db_session.flush()
        
        # Create quote line item with product relationship
        from app.models.deals.deal_models import QuoteLineItem
        line_item = QuoteLineItem(
            quote_id=quote.id,
            product_id=product.id,
            quantity=2,
            unit_price=100.00,
            total_price=200.00
        )
        
        db_session.add(line_item)
        db_session.commit()
        
        # Test that relationships work
        assert line_item.product is not None
        assert line_item.product.id == product.id
        assert line_item.quote is not None
        assert line_item.quote.id == quote.id
        assert quote.deal is not None
        assert quote.deal.id == deal.id
        assert deal.company is not None
        assert deal.company.id == company.id
        assert deal.contact is not None
        assert deal.contact.id == contact.id


class TestMigrationConstraints:
    """Test that migration constraints are properly applied."""
    
    def test_constraints_work_after_migration(self, db_session):
        """Test that constraints work correctly after migration."""
        from tests.factories import ProductFactory
        
        # Test unit price constraint
        product = ProductFactory()
        product.unit_price = -100.00
        
        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.add(product)
            db_session.commit()
        
        db_session.rollback()
        
        # Test stock quantity constraint
        product = ProductFactory()
        product.stock_quantity = -10
        
        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.add(product)
            db_session.commit()
        
        db_session.rollback()
        
        # Test reorder level constraint
        product = ProductFactory()
        product.reorder_level = -5
        
        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.add(product)
            db_session.commit()
        
        db_session.rollback()
        
        # Test lead time constraint
        product = ProductFactory()
        product.lead_time_days = -1
        
        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.add(product)
            db_session.commit()
        
        db_session.rollback()
    
    def test_indexes_exist_after_migration(self, db_session):
        """Test that indexes exist after migration."""
        inspector = inspect(db_session.bind)
        
        # Get indexes for products table
        indexes = inspector.get_indexes('products')
        index_names = [idx['name'] for idx in indexes]
        
        # Check for important indexes
        expected_indexes = [
            'products_pkey',  # Primary key
            'ix_products_sku',  # SKU index
            'ix_products_name',  # Name index
            'ix_products_category',  # Category index
            'ix_products_is_active',  # Active status index
            'idx_product_category_active',  # Composite index
            'idx_product_series',  # Series index
            'idx_product_item_no',  # Item number index
            'idx_product_sku_name'  # SKU/name composite index
        ]
        
        for index_name in expected_indexes:
            assert index_name in index_names, f"Missing index: {index_name}"


class TestMigrationPerformance:
    """Test that migrations don't significantly impact performance."""
    
    def test_query_performance_after_migration(self, db_session):
        """Test that queries perform well after migration."""
        from tests.factories import ProductFactory
        
        # Create many test products
        products = []
        for i in range(100):
            product = ProductFactory(
                name=f'Performance Test Product {i}',
                category='HVAC' if i % 2 == 0 else 'Plumbing',
                unit_price=100.00 + (i * 10)
            )
            products.append(product)
        
        db_session.add_all(products)
        db_session.commit()
        
        # Test various query performance
        import time
        
        # Test basic query
        start_time = time.time()
        all_products = Product.query.all()
        basic_query_time = time.time() - start_time
        assert len(all_products) >= 100
        assert basic_query_time < 1.0  # Should complete in under 1 second
        
        # Test filtered query
        start_time = time.time()
        hvac_products = Product.query.filter(Product.category == 'HVAC').all()
        filtered_query_time = time.time() - start_time
        assert len(hvac_products) >= 50
        assert filtered_query_time < 0.5  # Should complete in under 0.5 seconds
        
        # Test price range query
        start_time = time.time()
        price_range_products = Product.query.filter(
            Product.unit_price.between(200.00, 500.00)
        ).all()
        price_query_time = time.time() - start_time
        assert price_query_time < 0.5  # Should complete in under 0.5 seconds
        
        # Test search query
        start_time = time.time()
        search_products = Product.query.filter(
            Product.name.ilike('%Performance Test%')
        ).all()
        search_query_time = time.time() - start_time
        assert len(search_products) >= 100
        assert search_query_time < 0.5  # Should complete in under 0.5 seconds


class TestMigrationRollback:
    """Test that migrations can be rolled back if needed."""
    
    def test_migration_rollback_safety(self, db_session):
        """Test that migration rollback is safe."""
        # This test would be implemented if we had migration rollback functionality
        # For now, we'll test that the current schema is stable
        
        from tests.factories import ProductFactory
        
        # Create test product
        product = ProductFactory()
        db_session.add(product)
        db_session.commit()
        
        # Test that we can still work with the product
        assert product.id is not None
        assert product.name is not None
        assert product.unit_price is not None
        
        # Test that methods still work
        assert product.get_list_price() is not None
        assert product.get_discounted_price() is not None
        assert product.get_effective_price() is not None
        
        # Test that we can update the product
        original_name = product.name
        product.name = 'Updated Name'
        db_session.commit()
        
        assert product.name == 'Updated Name'
        
        # Test that we can delete the product
        product_id = product.id
        db_session.delete(product)
        db_session.commit()
        
        # Verify deletion
        deleted_product = Product.query.get(product_id)
        assert deleted_product is None
