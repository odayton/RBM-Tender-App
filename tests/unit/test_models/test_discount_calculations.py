"""
Unit tests for discount calculations and pricing logic
"""

import pytest
from decimal import Decimal
from app.models.deals.deal_models import Discount, QuoteLineItem, Quote, QuoteOption
from app.models.products.product_model import Product
from tests.factories import ProductFactory, QuoteFactory, QuoteOptionFactory, QuoteLineItemFactory


class TestDiscountCalculations:
    """Test discount calculation logic."""
    
    def test_product_discount_calculation(self, db_session):
        """Test product discount price calculation."""
        # Create product with discount
        product = ProductFactory(list_price=Decimal('1000.00'))
        discount = Discount(
            code='TEST10',
            percentage=Decimal('10.00'),
            description='10% test discount',
            is_active=True
        )
        db_session.add(discount)
        db_session.flush()
        
        product.discount_code = discount.code
        db_session.add(product)
        db_session.commit()
        
        # Test discounted price calculation
        discounted_price = product.get_discounted_price()
        expected_price = Decimal('900.00')  # 1000 - 10%
        
        assert discounted_price == expected_price
    
    def test_product_no_discount_calculation(self, db_session):
        """Test product price when no discount applied."""
        product = ProductFactory(list_price=Decimal('1000.00'))
        db_session.add(product)
        db_session.commit()
        
        # Test price without discount
        price = product.get_discounted_price()
        assert price == Decimal('1000.00')
    
    def test_product_inactive_discount_calculation(self, db_session):
        """Test product price when discount is inactive."""
        product = ProductFactory(list_price=Decimal('1000.00'))
        discount = Discount(
            code='INACTIVE',
            percentage=Decimal('20.00'),
            description='Inactive discount',
            is_active=False
        )
        db_session.add(discount)
        db_session.flush()
        
        product.discount_code = discount.code
        db_session.add(product)
        db_session.commit()
        
        # Test price with inactive discount (should return full price)
        price = product.get_discounted_price()
        assert price == Decimal('1000.00')
    
    def test_line_item_discount_calculation(self, db_session):
        """Test line item total price with discount."""
        product = ProductFactory(unit_price=Decimal('500.00'))
        db_session.add(product)
        db_session.commit()
        
        # Create quote first
        from app.models.deals.deal_models import QuoteRecipient
        from app.models.customers.company_model import Company
        
        company = Company(company_name='Test Company Grand Total')
        db_session.add(company)
        db_session.flush()
        
        # Create a deal first (required for QuoteRecipient)
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        user = User(username='testuser', email='test@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        deal = Deal(
            project_name='Test Project',
            deal_type=DealType.HVAC,
            state=AustralianState.NSW,
            stage=DealStage.SALES_LEAD,
            owner_id=user.id,
            total_amount=50000.00
        )
        db_session.add(deal)
        db_session.flush()
        
        recipient = QuoteRecipient(
            deal_id=deal.id,
            company_id=company.id,
            contact_person='Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option with quote_id
        option = QuoteOption(quote_id=quote.id, name='Test Option', freight_charge=Decimal('0.00'))
        db_session.add(option)
        db_session.flush()
        
        line_item = QuoteLineItem(
            option_id=option.id,
            product_id=product.id,
            quantity=2,
            unit_price=Decimal('500.00'),
            discount=Decimal('15.00')  # 15% discount
        )
        db_session.add(line_item)
        db_session.commit()
        
        # Test total price calculation
        total_price = line_item.total_price
        # Subtotal: 2 × 500 = 1000
        # Discount: 1000 × 15% = 150
        # Total: 1000 - 150 = 850
        expected_total = Decimal('850.00')
        
        assert total_price == expected_total
    
    def test_quote_grand_total_calculation(self, db_session):
        """Test quote grand total with discount."""
        # Create quote recipient first
        from app.models.deals.deal_models import QuoteRecipient
        from app.models.customers.company_model import Company
        
        company = Company(company_name='Test Company Grand Total Unique')
        db_session.add(company)
        db_session.flush()
        
        # Create a deal first (required for QuoteRecipient)
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        user = User(username='grandtotaluser', email='grandtotal@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        deal = Deal(
            project_name='Grand Total Test Project',
            deal_type=DealType.HVAC,
            state=AustralianState.NSW,
            stage=DealStage.SALES_LEAD,
            owner_id=user.id,
            total_amount=50000.00
        )
        db_session.add(deal)
        db_session.flush()
        
        recipient = QuoteRecipient(
            deal_id=deal.id,
            company_id=company.id,
            contact_person='Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote with discount
        quote = Quote(
            recipient_id=recipient.id,
            revision=1,
            total_discount=Decimal('5.00')  # 5% quote discount
        )
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option
        option = QuoteOption(
            quote_id=quote.id,
            name='Test Option',
            freight_charge=Decimal('100.00')
        )
        db_session.add(option)
        db_session.flush()
        
        # Create products for line items
        product1 = Product(item_no='GRAND-TOTAL-TEST-001', description='Grand Total Test Product 1', list_price=Decimal('1000.00'), category='Test', is_active=True)
        product2 = Product(item_no='GRAND-TOTAL-TEST-002', description='Grand Total Test Product 2', list_price=Decimal('500.00'), category='Test', is_active=True)
        db_session.add_all([product1, product2])
        db_session.flush()
        
        # Add line items
        line_item1 = QuoteLineItem(
            option_id=option.id,
            product_id=product1.id,
            quantity=1,
            unit_price=Decimal('1000.00'),
            discount=Decimal('0.00')
        )
        line_item2 = QuoteLineItem(
            option_id=option.id,
            product_id=product2.id,
            quantity=2,
            unit_price=Decimal('500.00'),
            discount=Decimal('10.00')  # 10% discount
        )
        db_session.add_all([line_item1, line_item2])
        db_session.commit()
        
        # Test grand total calculation
        grand_total = quote.grand_total
        # Line item 1: 1000 (no discount)
        # Line item 2: 2 × 500 - 10% = 900
        # Subtotal: 1000 + 900 = 1900
        # Freight: 100
        # Total before quote discount: 2000
        # Quote discount: 2000 × 5% = 100
        # Grand total: 2000 - 100 = 1900
        expected_total = Decimal('1900.00')
        
        assert grand_total == expected_total
    
    def test_discount_validation(self, db_session):
        """Test discount validation rules."""
        # Test valid discount
        discount = Discount(
            code='VALID',
            percentage=Decimal('25.00'),
            description='Valid discount',
            is_active=True
        )
        db_session.add(discount)
        db_session.commit()
        assert discount.validate() is None
        
        # Test invalid percentage (over 100%)
        discount.percentage = Decimal('150.00')
        with pytest.raises(Exception):  # Should raise ValidationError
            discount.validate()
        
        # Test invalid percentage (negative)
        discount.percentage = Decimal('-10.00')
        with pytest.raises(Exception):  # Should raise ValidationError
            discount.validate()
    
    def test_discount_code_uniqueness(self, db_session):
        """Test that discount codes must be unique."""
        discount1 = Discount(code='UNIQUE', percentage=Decimal('10.00'), is_active=True)
        discount2 = Discount(code='UNIQUE', percentage=Decimal('20.00'), is_active=True)
        
        db_session.add(discount1)
        db_session.commit()
        
        db_session.add(discount2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()


class TestProductStatus:
    """Test product status logic."""
    
    def test_active_status(self, db_session):
        """Test active product status."""
        product = ProductFactory(is_active=True)
        db_session.add(product)
        db_session.commit()
        
        assert product.is_active is True
    
    def test_inactive_status(self, db_session):
        """Test inactive product status."""
        product = ProductFactory(is_active=False)
        db_session.add(product)
        db_session.commit()
        
        assert product.is_active is False


class TestBusinessLogicValidation:
    """Test business logic validation rules."""
    
    def test_deal_stage_progression(self, db_session):
        """Test deal stage validation."""
        from app.models.deals.deal_models import Deal, DealStage, DealType, AustralianState
        from tests.factories import UserFactory
        
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        deal = Deal(
            project_name='Test Deal',
            stage=DealStage.SALES_LEAD,
            deal_type=DealType.HVAC,
            state=AustralianState.NSW,
            owner_id=user.id
        )
        db_session.add(deal)
        db_session.commit()
        
        # Test valid stage
        assert deal.stage == DealStage.SALES_LEAD
        
        # Test stage progression
        deal.stage = DealStage.PROPOSAL
        db_session.commit()
        assert deal.stage == DealStage.PROPOSAL
    
    def test_quote_status_transitions(self, db_session):
        """Test quote status validation."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Status Transitions Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='statustransitionsuser', email='statustransitions@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Status Transitions Test Project',
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
            contact_person='Status Transitions Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote with draft status
        quote = Quote(recipient_id=recipient.id, revision=1, status='draft')
        db_session.add(quote)
        db_session.commit()
        
        # Test valid status transitions
        valid_statuses = ['draft', 'sent', 'accepted', 'rejected']
        for status in valid_statuses:
            quote.status = status
            db_session.commit()
            assert quote.status == status
    
    def test_user_permission_checks(self, db_session):
        """Test user permission checking."""
        from tests.factories import AdminUserFactory, SalesUserFactory
        
        admin = AdminUserFactory()
        sales_user = SalesUserFactory()
        db_session.add_all([admin, sales_user])
        db_session.commit()
        
        # Test admin permissions
        assert admin.can_manage_users() is True
        assert admin.can_view_admin_panel() is True
        
        # Test sales user permissions
        assert sales_user.can_manage_users() is False
        assert sales_user.can_view_admin_panel() is False
