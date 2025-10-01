"""
Product Integration Tests

These tests validate that product endpoints work correctly with the current schema.
They catch issues with routes that fail due to schema problems.
"""

import pytest
from flask import url_for
from tests.factories import ProductFactory, AdminUserFactory


class TestProductEndpointsIntegration:
    """Test product endpoints with real database interactions."""
    
    def test_product_list_endpoint(self, client, db_session):
        """Test that product list endpoint works with current schema."""
        # Create test products
        product1 = ProductFactory(category='HVAC', unit_price=100.00)
        product2 = ProductFactory(category='Plumbing', unit_price=200.00)
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product list endpoint
        response = client.get('/products/')
        assert response.status_code == 200
        assert b'products' in response.data.lower()
        
        # Check that products are displayed
        assert product1.name.encode() in response.data
        assert product2.name.encode() in response.data
    
    def test_product_create_endpoint(self, client, db_session):
        """Test that product creation works with current schema."""
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product creation form
        response = client.get('/products/create')
        assert response.status_code == 200
        assert b'Create Product' in response.data
        
        # Test product creation
        response = client.post('/products/create', data={
            'category': 'Test Category',
            'item_no': 'TEST-001',
            'description': 'Test Product Description',
            'nett': '100.00',
            'is_active': True
        }, follow_redirects=True)
        
        # Should either succeed or redirect (not 500 error)
        assert response.status_code in [200, 302], f"Unexpected status code: {response.status_code}"
        
        # Check that product was created
        from app.models.products.product_model import Product
        product = Product.query.filter_by(item_no='TEST-001').first()
        assert product is not None
        assert product.category == 'Test Category'
    
    def test_product_edit_endpoint(self, client, db_session):
        """Test that product editing works with current schema."""
        # Create test product
        product = ProductFactory()
        db_session.add(product)
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product edit form
        response = client.get(f'/products/{product.id}/edit')
        assert response.status_code == 200
        assert b'Edit Product' in response.data
        
        # Test product update
        response = client.post(f'/products/{product.id}/edit', data={
            'category': 'Updated Category',
            'item_no': product.item_no,
            'description': 'Updated Description',
            'nett': '150.00',
            'is_active': True
        }, follow_redirects=True)
        
        # Should either succeed or redirect (not 500 error)
        assert response.status_code in [200, 302], f"Unexpected status code: {response.status_code}"
        
        # Check that product was updated
        db_session.refresh(product)
        assert product.category == 'Updated Category'
    
    def test_product_view_endpoint(self, client, db_session):
        """Test that product view works with current schema."""
        # Create test product
        product = ProductFactory()
        db_session.add(product)
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product view
        response = client.get(f'/products/{product.id}')
        assert response.status_code == 200
        assert product.name.encode() in response.data
        assert product.description.encode() in response.data
    
    def test_product_search_endpoint(self, client, db_session):
        """Test that product search works with current schema."""
        # Create test products
        product1 = ProductFactory(name='HVAC Unit', category='HVAC')
        product2 = ProductFactory(name='Plumbing Fixture', category='Plumbing')
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product search
        response = client.get('/products/?search_term=HVAC')
        assert response.status_code == 200
        assert b'HVAC Unit' in response.data
        assert b'Plumbing Fixture' not in response.data
    
    def test_product_filtering_endpoint(self, client, db_session):
        """Test that product filtering works with current schema."""
        # Create test products with different prices
        product1 = ProductFactory(unit_price=50.00, category='HVAC')
        product2 = ProductFactory(unit_price=500.00, category='Plumbing')
        product3 = ProductFactory(unit_price=1500.00, category='HVAC')
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test price range filtering
        response = client.get('/products/?price_range=0-100')
        assert response.status_code == 200
        # Should show product1 (price 50) but not product2 (price 500) or product3 (price 1500)
        
        # Test category filtering
        response = client.get('/products/?category=HVAC')
        assert response.status_code == 200
        # Should show HVAC products only
    
    def test_product_import_endpoint(self, client, db_session):
        """Test that product import works with current schema."""
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product import page
        response = client.get('/products/import')
        assert response.status_code == 200
        assert b'Import Products' in response.data
    
    def test_product_export_endpoint(self, client, db_session):
        """Test that product export works with current schema."""
        # Create test products
        product1 = ProductFactory()
        product2 = ProductFactory()
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product export
        response = client.get('/products/export')
        assert response.status_code == 200
        # Should return CSV or Excel file


class TestProductEndpointsErrorHandling:
    """Test that product endpoints handle errors gracefully."""
    
    def test_product_list_with_invalid_filters(self, client, db_session):
        """Test that product list handles invalid filters gracefully."""
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test with invalid price range
        response = client.get('/products/?price_range=invalid')
        assert response.status_code == 200  # Should not crash
        
        # Test with invalid category
        response = client.get('/products/?category=')
        assert response.status_code == 200  # Should not crash
    
    def test_product_view_nonexistent(self, client, db_session):
        """Test that product view handles nonexistent products gracefully."""
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test with nonexistent product ID
        response = client.get('/products/99999')
        assert response.status_code == 404  # Should return 404, not 500
    
    def test_product_edit_nonexistent(self, client, db_session):
        """Test that product edit handles nonexistent products gracefully."""
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test with nonexistent product ID
        response = client.get('/products/99999/edit')
        assert response.status_code == 404  # Should return 404, not 500


class TestProductEndpointsPerformance:
    """Test that product endpoints perform well with current schema."""
    
    def test_product_list_performance(self, client, db_session):
        """Test that product list performs well with many products."""
        # Create many test products
        products = []
        for i in range(50):
            product = ProductFactory(name=f'Product {i}')
            products.append(product)
        
        db_session.add_all(products)
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product list with many products
        import time
        start_time = time.time()
        response = client.get('/products/')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should load in under 2 seconds
    
    def test_product_search_performance(self, client, db_session):
        """Test that product search performs well."""
        # Create many test products
        products = []
        for i in range(100):
            product = ProductFactory(name=f'Searchable Product {i}')
            products.append(product)
        
        db_session.add_all(products)
        db_session.commit()
        
        # Create admin user and login
        admin_user = AdminUserFactory(password='password123')
        db_session.add(admin_user)
        db_session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'email': admin_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Test product search performance
        import time
        start_time = time.time()
        response = client.get('/products/?search_term=Searchable')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should search in under 1 second
