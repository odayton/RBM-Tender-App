"""
Unit tests for product business logic and inventory management
"""

import pytest
from decimal import Decimal
from app.models.products.product_model import Product
from app.models.deals.deal_models import Discount
from tests.factories import ProductFactory


class TestProductBusinessLogic:
    """Test product business logic."""
    
    def test_product_item_no_validation(self, db_session):
        """Test that product item numbers are validated."""
        # Test valid item number
        product = Product(
            item_no='VALID-ITEM-TEST-1',
            description='Test Product',
            category='Test',
            list_price=Decimal('100.00'),
            is_active=True
        )
        db_session.add(product)
        db_session.commit()
        
        assert product.item_no == 'VALID-ITEM-TEST-1'
        
        # Test empty item number (should fail validation)
        product.item_no = ''
        with pytest.raises(Exception):  # Should raise ValidationError
            product.validate()
    
    def test_product_description_validation(self, db_session):
        """Test product description validation."""
        # Test valid product description
        product = ProductFactory(description='Valid Product Description')
        db_session.add(product)
        db_session.commit()
        
        assert product.description == 'Valid Product Description'
        
        # Test empty description (should fail validation)
        product.description = ''
        with pytest.raises(Exception):  # Should raise ValidationError
            product.validate()
    
    def test_product_price_validation(self, db_session):
        """Test product price validation."""
        # Test valid price
        product = ProductFactory(list_price=Decimal('100.00'))
        db_session.add(product)
        db_session.commit()
        
        assert product.list_price == Decimal('100.00')
        
        # Test negative price (should fail validation)
        product.list_price = Decimal('-50.00')
        with pytest.raises(Exception):  # Should raise ValidationError
            product.validate()
    
    def test_product_carton_qty_validation(self, db_session):
        """Test product carton quantity validation."""
        # Test valid carton quantity
        product = ProductFactory(carton_qty=10)
        db_session.add(product)
        db_session.commit()
        
        assert product.carton_qty == 10
        
        # Test negative carton quantity (should fail validation)
        product.carton_qty = -5
        with pytest.raises(Exception):  # Should raise ValidationError
            product.validate()
    
    def test_product_lead_time_validation(self, db_session):
        """Test product lead time validation."""
        # Test valid lead time
        product = ProductFactory(lead_time_days=5)
        db_session.add(product)
        db_session.commit()
        
        assert product.lead_time_days == 5
        
        # Test negative lead time (should fail validation)
        product.lead_time_days = -2
        with pytest.raises(Exception):  # Should raise ValidationError
            product.validate()
    
    def test_product_weight_validation(self, db_session):
        """Test product weight validation."""
        # Test valid weight
        product = ProductFactory(weight_kg=Decimal('10.5'))
        db_session.add(product)
        db_session.commit()
        
        assert product.weight_kg == Decimal('10.5')
        
        # Test negative weight (should fail validation)
        product.weight_kg = Decimal('-5.0')
        with pytest.raises(Exception):  # Should raise ValidationError
            product.validate()
    
    def test_product_category_indexing(self, db_session):
        """Test product category indexing."""
        product1 = ProductFactory(category='HVAC')
        product2 = ProductFactory(category='Plumbing')
        product3 = ProductFactory(category='HVAC')
        
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Test category filtering
        hvac_products = db_session.query(Product).filter_by(category='HVAC').all()
        assert len(hvac_products) == 2
        
        plumbing_products = db_session.query(Product).filter_by(category='Plumbing').all()
        assert len(plumbing_products) == 1
    
    def test_product_series_indexing(self, db_session):
        """Test product series indexing."""
        product1 = ProductFactory(series='Series A')
        product2 = ProductFactory(series='Series B')
        product3 = ProductFactory(series='Series A')
        
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Test series filtering
        series_a_products = db_session.query(Product).filter_by(series='Series A').all()
        assert len(series_a_products) == 2
        
        series_b_products = db_session.query(Product).filter_by(series='Series B').all()
        assert len(series_b_products) == 1
    
    def test_product_active_status_indexing(self, db_session):
        """Test product active status indexing."""
        # Create products with specific active status
        product1 = Product(
            item_no='ACTIVE-TEST-1',
            description='Active Product 1',
            category='Test',
            list_price=Decimal('100.00'),
            is_active=True
        )
        product2 = Product(
            item_no='INACTIVE-TEST-1',
            description='Inactive Product 1',
            category='Test',
            list_price=Decimal('200.00'),
            is_active=False
        )
        product3 = Product(
            item_no='ACTIVE-TEST-2',
            description='Active Product 2',
            category='Test',
            list_price=Decimal('300.00'),
            is_active=True
        )

        db_session.add_all([product1, product2, product3])
        db_session.commit()

        # Test active status filtering - should only find our 2 active products
        active_products = db_session.query(Product).filter_by(is_active=True).filter(Product.item_no.like('ACTIVE-TEST-%')).all()
        assert len(active_products) == 2
        
        inactive_products = db_session.query(Product).filter_by(is_active=False).all()
        assert len(inactive_products) == 1
    
    def test_product_usage_count(self, db_session):
        """Test product usage count calculation."""
        # Create product directly
        product = Product(
            item_no='USAGE-TEST-1',
            description='Usage Test Product',
            category='Test',
            list_price=Decimal('100.00'),
            is_active=True
        )
        db_session.add(product)
        db_session.commit()
        
        # Initially no usage
        assert len(product.line_items) == 0
        
        # Create the full hierarchy for line items
        from app.models.deals.deal_models import QuoteLineItem, QuoteRecipient, Quote, QuoteOption
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole

        # Create company
        company = Company(company_name='Usage Test Company')
        db_session.add(company)
        db_session.flush()

        # Create user
        user = User(username='usageuser', email='usage@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()

        # Create deal
        deal = Deal(
            project_name='Usage Test Project',
            deal_type=DealType.HVAC,
            state=AustralianState.NSW,
            stage=DealStage.SALES_LEAD,
            owner_id=user.id,
            total_amount=50000.00
        )
        db_session.add(deal)
        db_session.flush()

        # Create quote recipient
        recipient = QuoteRecipient(
            deal_id=deal.id,
            company_id=company.id,
            contact_person='Usage Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()

        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()

        # Create quote option
        option = QuoteOption(
            quote_id=quote.id,
            name='Usage Test Option',
            freight_charge=Decimal('0.00')
        )
        db_session.add(option)
        db_session.flush()
        
        line_item = QuoteLineItem(
            option_id=option.id,
            product_id=product.id,
            quantity=1,
            unit_price=product.list_price
        )
        db_session.add(line_item)
        db_session.commit()
        
        # Test usage count
        assert len(product.line_items) == 1
    
    def test_product_to_dict_conversion(self, db_session):
        """Test product to dictionary conversion."""
        discount = Discount(
            code='TEST20',
            percentage=Decimal('20.00'),
            description='Test discount',
            is_active=True
        )
        db_session.add(discount)
        db_session.flush()
        
        product = ProductFactory(
            list_price=Decimal('1000.00'),
            discount_code=discount.code
        )
        db_session.add(product)
        db_session.commit()
        
        # Test dictionary conversion
        product_dict = product.to_dict()
        
        assert 'discount_percentage' in product_dict
        assert product_dict['discount_percentage'] == 20.0
        
        assert 'discounted_price' in product_dict
        assert product_dict['discounted_price'] == 800.0  # 1000 - 20%
        
        # Stock-related fields removed from new schema
        
        assert 'usage_count' in product_dict
        assert product_dict['usage_count'] == 0  # No line items yet
    
    def test_product_list_price(self, db_session):
        """Test product list price."""
        # Test list price
        product1 = ProductFactory(
            list_price=Decimal('1000.00')
        )
        db_session.add(product1)
        db_session.commit()
        
        assert product1.list_price == Decimal('1000.00')
        
        # Test with different list price
        product2 = ProductFactory(
            list_price=Decimal('500.00')
        )
        db_session.add(product2)
        db_session.commit()
        
        assert product2.list_price == Decimal('500.00')
    
    
    def test_product_dimensions_formatting(self, db_session):
        """Test product dimensions formatting."""
        product = ProductFactory(dimensions='100x50x25cm')
        db_session.add(product)
        db_session.commit()
        
        assert product.dimensions == '100x50x25cm'
    
    def test_product_pack_formatting(self, db_session):
        """Test product pack formatting."""
        product = ProductFactory(pack='PACK-123')
        db_session.add(product)
        db_session.commit()
        
        assert product.pack == 'PACK-123'
    
    def test_product_notes_functionality(self, db_session):
        """Test product notes functionality."""
        product = ProductFactory(notes='Product notes')
        db_session.add(product)
        db_session.commit()
        
        assert product.notes == 'Product notes'
        
        # Update notes
        product.notes = 'Updated product notes'
        db_session.commit()
        
        assert product.notes == 'Updated product notes'
