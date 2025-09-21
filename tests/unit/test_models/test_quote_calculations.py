"""
Unit tests for quote calculations and pricing logic
"""

import pytest
from decimal import Decimal
from app.models.deals.deal_models import Quote, QuoteOption, QuoteLineItem
from tests.factories import QuoteFactory, QuoteOptionFactory, QuoteLineItemFactory, ProductFactory


class TestQuoteCalculations:
    """Test quote calculation logic."""
    
    def test_quote_option_total_price(self, db_session):
        """Test quote option total price calculation."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption, QuoteLineItem
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        from app.models.products.product_model import Product
        
        # Create company
        company = Company(company_name='Quote Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='quoteuser', email='quote@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Quote Test Project',
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
            contact_person='Quote Test Contact',
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
            name='Test Option',
            freight_charge=Decimal('150.00')
        )
        db_session.add(option)
        db_session.flush()
        
        # Create products
        product1 = Product(sku='QUOTE-TEST-1', name='Test Product 1', unit_price=Decimal('1000.00'), is_active=True)
        product2 = Product(sku='QUOTE-TEST-2', name='Test Product 2', unit_price=Decimal('500.00'), is_active=True)
        db_session.add_all([product1, product2])
        db_session.flush()
        
        # Add line items
        line_item1 = QuoteLineItem(
            option_id=option.id,
            product_id=product1.id,
            quantity=2,
            unit_price=Decimal('1000.00'),
            discount=Decimal('0.00')
        )
        line_item2 = QuoteLineItem(
            option_id=option.id,
            product_id=product2.id,
            quantity=1,
            unit_price=Decimal('500.00'),
            discount=Decimal('10.00')  # 10% discount
        )
        db_session.add_all([line_item1, line_item2])
        db_session.commit()
        
        # Test total price calculation
        total_price = option.total_price
        # Line item 1: 2 × 1000 = 2000
        # Line item 2: 1 × 500 - 10% = 450
        # Subtotal: 2000 + 450 = 2450
        # Freight: 150
        # Total: 2450 + 150 = 2600
        expected_total = Decimal('2600.00')
        
        assert total_price == expected_total
    
    def test_quote_total_price_multiple_options(self, db_session):
        """Test quote total price with multiple options."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption, QuoteLineItem
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        from app.models.products.product_model import Product
        
        # Create company
        company = Company(company_name='Multi Option Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='multioptionuser', email='multioption@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Multi Option Test Project',
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
            contact_person='Multi Option Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create products
        product1 = Product(sku='MULTI-TEST-1', name='Multi Test Product 1', unit_price=Decimal('1000.00'), is_active=True)
        product2 = Product(sku='MULTI-TEST-2', name='Multi Test Product 2', unit_price=Decimal('750.00'), is_active=True)
        db_session.add_all([product1, product2])
        db_session.flush()
        
        # Create two options
        option1 = QuoteOption(
            quote_id=quote.id,
            name='Option 1',
            freight_charge=Decimal('100.00')
        )
        option2 = QuoteOption(
            quote_id=quote.id,
            name='Option 2',
            freight_charge=Decimal('200.00')
        )
        db_session.add_all([option1, option2])
        db_session.flush()
        
        # Add line items to option 1
        line_item1 = QuoteLineItem(
            option_id=option1.id,
            product_id=product1.id,
            quantity=1,
            unit_price=Decimal('1000.00'),
            discount=Decimal('0.00')
        )
        db_session.add(line_item1)
        db_session.flush()
        
        # Add line items to option 2
        line_item2 = QuoteLineItem(
            option_id=option2.id,
            product_id=product2.id,
            quantity=2,
            unit_price=Decimal('750.00'),
            discount=Decimal('5.00')  # 5% discount
        )
        db_session.add(line_item2)
        db_session.commit()
        
        # Test total price calculation
        total_price = quote.total_price
        # Option 1: 1000 + 100 = 1100
        # Option 2: (2 × 750 - 5%) + 200 = 1425 + 200 = 1625
        # Total: 1100 + 1625 = 2725
        expected_total = Decimal('2725.00')
        
        assert total_price == expected_total
    
    def test_quote_grand_total_with_discount(self, db_session):
        """Test quote grand total with quote-level discount."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption, QuoteLineItem
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        from app.models.products.product_model import Product
        
        # Create company
        company = Company(company_name='Grand Total Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='grandtotaldiscountuser', email='grandtotaldiscount@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
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
        
        # Create quote recipient
        recipient = QuoteRecipient(
            deal_id=deal.id,
            company_id=company.id,
            contact_person='Grand Total Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote with discount
        quote = Quote(recipient_id=recipient.id, revision=1, total_discount=Decimal('8.00'))  # 8% quote discount
        db_session.add(quote)
        db_session.flush()
        
        # Create product
        product = Product(sku='GRAND-TEST-1', name='Grand Total Test Product', unit_price=Decimal('1000.00'), is_active=True)
        db_session.add(product)
        db_session.flush()
        
        # Create quote option
        option = QuoteOption(
            quote_id=quote.id,
            name='Grand Total Option',
            freight_charge=Decimal('250.00')
        )
        db_session.add(option)
        db_session.flush()
        
        # Add line items
        line_item = QuoteLineItem(
            option_id=option.id,
            product_id=product.id,
            quantity=3,
            unit_price=Decimal('1000.00'),
            discount=Decimal('0.00')
        )
        db_session.add(line_item)
        db_session.commit()
        
        # Test grand total calculation
        grand_total = quote.grand_total
        # Line item: 3 × 1000 = 3000
        # Freight: 250
        # Subtotal: 3000 + 250 = 3250
        # Quote discount: 3250 × 8% = 260
        # Grand total: 3250 - 260 = 2990
        expected_total = Decimal('2990.00')
        
        assert grand_total == expected_total
    
    def test_line_item_custom_product(self, db_session):
        """Test line item with custom product (no product_id)."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption, QuoteLineItem
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Custom Product Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='customproductuser', email='customproduct@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Custom Product Test Project',
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
            contact_person='Custom Product Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option
        option = QuoteOption(quote_id=quote.id, name='Custom Product Option')
        db_session.add(option)
        db_session.flush()
        
        # Create line item with custom product (no product_id)
        line_item = QuoteLineItem(
            option_id=option.id,
            product_id=None,  # No product
            custom_sku='CUSTOM-001',
            custom_name='Custom Product',
            custom_description='Custom product description',
            quantity=1,
            unit_price=Decimal('1500.00'),
            discount=Decimal('0.00')
        )
        db_session.add(line_item)
        db_session.commit()
        
        # Test custom product properties
        assert line_item.product_sku == 'CUSTOM-001'
        assert line_item.product_name == 'Custom Product'
        assert line_item.total_price == Decimal('1500.00')
    
    def test_line_item_display_order(self, db_session):
        """Test line item display order functionality."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption, QuoteLineItem
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        from app.models.products.product_model import Product
        
        # Create company
        company = Company(company_name='Display Order Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='displayorderuser', email='displayorder@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Display Order Test Project',
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
            contact_person='Display Order Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option
        option = QuoteOption(quote_id=quote.id, name='Display Order Option')
        db_session.add(option)
        db_session.flush()
        
        # Create products
        product1 = Product(sku='DISPLAY-TEST-1', name='Display Test Product 1', unit_price=Decimal('100.00'), is_active=True)
        product2 = Product(sku='DISPLAY-TEST-2', name='Display Test Product 2', unit_price=Decimal('200.00'), is_active=True)
        product3 = Product(sku='DISPLAY-TEST-3', name='Display Test Product 3', unit_price=Decimal('300.00'), is_active=True)
        db_session.add_all([product1, product2, product3])
        db_session.flush()
        
        # Create line items with specific display orders
        line_item1 = QuoteLineItem(
            option_id=option.id,
            product_id=product1.id,
            display_order=2,
            quantity=1,
            unit_price=Decimal('100.00')
        )
        line_item2 = QuoteLineItem(
            option_id=option.id,
            product_id=product2.id,
            display_order=1,
            quantity=1,
            unit_price=Decimal('200.00')
        )
        line_item3 = QuoteLineItem(
            option_id=option.id,
            product_id=product3.id,
            display_order=3,
            quantity=1,
            unit_price=Decimal('300.00')
        )
        db_session.add_all([line_item1, line_item2, line_item3])
        db_session.commit()
        
        # Test that display order is preserved
        assert line_item1.display_order == 2
        assert line_item2.display_order == 1
        assert line_item3.display_order == 3
    
    def test_quote_revision_numbering(self, db_session):
        """Test quote revision numbering."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Revision Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='revisionuser', email='revision@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Revision Test Project',
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
            contact_person='Revision Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create multiple quotes for same recipient
        quote1 = Quote(recipient_id=recipient.id, revision=1)
        quote2 = Quote(recipient_id=recipient.id, revision=2)
        quote3 = Quote(recipient_id=recipient.id, revision=3)
        
        db_session.add_all([quote1, quote2, quote3])
        db_session.commit()
        
        # Test revision numbers
        assert quote1.revision == 1
        assert quote2.revision == 2
        assert quote3.revision == 3
    
    def test_quote_status_validation(self, db_session):
        """Test quote status validation."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Status Validation Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='statususer', email='status@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Status Validation Test Project',
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
            contact_person='Status Validation Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote with draft status
        quote = Quote(recipient_id=recipient.id, revision=1, status='draft')
        db_session.add(quote)
        db_session.commit()
        
        # Test valid statuses
        valid_statuses = ['draft', 'sent', 'accepted', 'rejected']
        for status in valid_statuses:
            quote.status = status
            db_session.commit()
            assert quote.status == status
    
    def test_quote_valid_until_date(self, db_session):
        """Test quote validity date functionality."""
        from datetime import datetime, timedelta
        
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Valid Until Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='validuntiluser', email='validuntil@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Valid Until Test Project',
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
            contact_person='Valid Until Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.commit()
        
        # Test setting validity date
        valid_until = datetime.now() + timedelta(days=30)
        quote.valid_until = valid_until
        db_session.commit()
        
        # Test that the validity date was set (allow for small time differences)
        assert quote.valid_until is not None
        assert abs((quote.valid_until - valid_until).total_seconds()) < 5  # Within 5 seconds
    
    def test_quote_notes_functionality(self, db_session):
        """Test quote notes functionality."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Notes Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='notesuser', email='notes@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Notes Test Project',
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
            contact_person='Notes Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote with notes
        quote = Quote(recipient_id=recipient.id, revision=1, notes='Initial quote notes')
        db_session.add(quote)
        db_session.commit()
        
        assert quote.notes == 'Initial quote notes'
        
        # Update notes
        quote.notes = 'Updated quote notes'
        db_session.commit()
        
        assert quote.notes == 'Updated quote notes'
    
    def test_quote_option_lead_time_display(self, db_session):
        """Test quote option lead time display."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Lead Time Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='leadtimeuser', email='leadtime@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Lead Time Test Project',
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
            contact_person='Lead Time Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option with lead time
        option = QuoteOption(quote_id=quote.id, name='Lead Time Option', lead_time_value='15', lead_time_unit='days')
        db_session.add(option)
        db_session.commit()
        
        # Test lead time display
        lead_time_display = option.lead_time_display
        assert '15' in lead_time_display
        assert 'days' in lead_time_display.lower()
        
        # Test with zero lead time
        option.lead_time_value = None
        option.lead_time_unit = None
        db_session.commit()
        
        lead_time_display = option.lead_time_display
        assert lead_time_display == "TBA"
    
    def test_quote_option_notes_functionality(self, db_session):
        """Test quote option notes functionality."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        
        # Create company
        company = Company(company_name='Option Notes Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='optionnotesuser', email='optionnotes@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Option Notes Test Project',
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
            contact_person='Option Notes Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option with description
        option = QuoteOption(quote_id=quote.id, name='Option Notes Option', description='Option notes')
        db_session.add(option)
        db_session.commit()
        
        assert option.description == 'Option notes'
        
        # Update description
        option.description = 'Updated option notes'
        db_session.commit()
        
        assert option.description == 'Updated option notes'
    
    def test_line_item_notes_functionality(self, db_session):
        """Test line item notes functionality."""
        # Create the full hierarchy
        from app.models.deals.deal_models import QuoteRecipient, Quote, QuoteOption, QuoteLineItem
        from app.models.customers.company_model import Company
        from app.models import Deal, DealType, DealStage, AustralianState
        from app.models.user_model import User, UserRole
        from app.models.products.product_model import Product
        
        # Create company
        company = Company(company_name='Line Item Notes Test Company')
        db_session.add(company)
        db_session.flush()
        
        # Create user
        user = User(username='lineitemnotesuser', email='lineitemnotes@example.com', role=UserRole.SALES, is_active=True)
        user.password = 'password123'
        db_session.add(user)
        db_session.flush()
        
        # Create deal
        deal = Deal(
            project_name='Line Item Notes Test Project',
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
            contact_person='Line Item Notes Test Contact',
            delivery_method='email'
        )
        db_session.add(recipient)
        db_session.flush()
        
        # Create quote
        quote = Quote(recipient_id=recipient.id, revision=1)
        db_session.add(quote)
        db_session.flush()
        
        # Create quote option
        option = QuoteOption(quote_id=quote.id, name='Line Item Notes Option')
        db_session.add(option)
        db_session.flush()
        
        # Create product
        product = Product(sku='LINEITEM-NOTES-TEST-1', name='Line Item Notes Test Product', unit_price=Decimal('1000.00'), is_active=True)
        db_session.add(product)
        db_session.flush()
        
        # Create line item with notes
        line_item = QuoteLineItem(
            option_id=option.id,
            product_id=product.id,
            quantity=1,
            unit_price=Decimal('1000.00'),
            notes='Line item notes'
        )
        db_session.add(line_item)
        db_session.commit()
        
        assert line_item.notes == 'Line item notes'
        
        # Update notes
        line_item.notes = 'Updated line item notes'
        db_session.commit()
        
        assert line_item.notes == 'Updated line item notes'
