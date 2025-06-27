import logging
from app import create_app
from app.extensions import db
from app.models import (
    User, UserRole, Company, Contact, Product,
    Deal, DealStage, DealType, AustralianState,
    Quote, QuoteRecipient, QuoteOption, QuoteLineItem,
    Pump, PumpAssembly, InertiaBase, SeismicSpring, RubberMount
)

# Use the configured logger from the application
logger = logging.getLogger(__name__)

def seed_database():
    """Seeds the database with initial data in an idempotent way."""
    logger.info("Starting database seeding process...")

    # --- Clear Data ---
    logger.info("Clearing existing data...")
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        logger.info(f'Clearing table {table.name}')
        db.session.execute(table.delete())
    db.session.commit()
    logger.info("Data cleared.")

    # --- Seed Users ---
    logger.info("Seeding users...")
    admin_user = User(username='admin', email='admin@example.com', first_name='Admin', last_name='User', role=UserRole.ADMIN, is_active=True)
    admin_user.password = 'password'
    dev_user = User(username='devuser', email='dev@example.com', first_name='Dev', last_name='User', role=UserRole.SALES, is_active=True)
    dev_user.password = 'password'
    db.session.add_all([admin_user, dev_user])
    db.session.commit()
    logger.info("Seeded users.")

    # --- Seed Companies, Contacts, and other base data ---
    logger.info("Seeding companies, contacts, and pump data...")
    company1 = Company(company_name='ACME Mechanical', address='123 Industrial Way, Sydney NSW')
    company2 = Company(company_name='Fluid Solutions Inc.', address='456 Pumping St, Melbourne VIC')
    db.session.add_all([company1, company2])
    db.session.commit()

    contact1 = Contact(name='John Smith', email='john.s@acme.com', phone_number='0411222333', company_id=company1.id)
    contact2 = Contact(name='Jane Doe', email='jane.d@fluidsolutions.com', phone_number='0422333444', company_id=company2.id)
    db.session.add_all([contact1, contact2])
    db.session.commit()
    
    pump1 = Pump(pump_model='TestPump-A', nominal_flow=10.0, nominal_head=50.0)
    db.session.add(pump1)
    db.session.commit()
    assembly1 = PumpAssembly(pump_id=pump1.id, assembly_name='PMP-TEST-001')
    db.session.add(assembly1)
    db.session.commit()
    product1 = Product(sku=assembly1.assembly_name, name=f"Assembly for {assembly1.pump.pump_model}", unit_price=2500.00, pump_assembly_id=assembly1.id)
    custom_product = Product(sku="LAB-01", name="Custom Labour Charge", unit_price=150.00)
    db.session.add_all([product1, custom_product])
    db.session.commit()
    logger.info("Seeded base data.")

    # --- Seed Deals ---
    logger.info("Seeding deals...")
    # Deal 1: The fully detailed deal
    deal1 = Deal(project_name='City Hospital HVAC Upgrade', owner_id=dev_user.id, stage=DealStage.PROPOSAL, deal_type=DealType.HVAC, state=AustralianState.NSW)
    deal1.companies.append(company1)
    deal1.contacts.append(contact1)
    db.session.add(deal1)
    db.session.commit()

    # Other deals for variety
    deal2 = Deal(project_name='Downtown Tower Plumbing', owner_id=dev_user.id, stage=DealStage.TENDER, deal_type=DealType.HYDRAULIC, state=AustralianState.VIC, companies=[company2], contacts=[contact2])
    db.session.add(deal2)
    db.session.commit()
    
    # --- Create the Quote Stream (Recipient) for Deal 1 ---
    recipient1 = QuoteRecipient(deal_id=deal1.id, company_id=company1.id)
    db.session.add(recipient1)
    db.session.commit()

    # --- Create Revision 1 for Deal 1 ---
    quote_rev1 = Quote(recipient_id=recipient1.id, revision=1, notes="Initial proposal based on preliminary drawings.")
    db.session.add(quote_rev1)
    db.session.commit()

    # Option 1: Standard Offer
    option1_1 = QuoteOption(quote_id=quote_rev1.id, name="Standard Offer", freight_charge=500.00)
    db.session.add(option1_1)
    db.session.commit()
    line_item1_1_1 = QuoteLineItem(option_id=option1_1.id, product_id=product1.id, quantity=2, unit_price=2500.00, discount=5.0, display_order=1, notes="CHWP")
    line_item1_1_2 = QuoteLineItem(option_id=option1_1.id, product_id=custom_product.id, quantity=8, unit_price=150.00, display_order=2, notes="Standard labour")
    db.session.add_all([line_item1_1_1, line_item1_1_2])
    
    # Option 2: Premium Offer
    option1_2 = QuoteOption(quote_id=quote_rev1.id, name="Premium Option (High Efficiency)", freight_charge=500.00)
    db.session.add(option1_2)
    db.session.commit()
    line_item1_2_1 = QuoteLineItem(option_id=option1_2.id, product_id=product1.id, quantity=2, unit_price=3200.00, discount=0.0, display_order=1, notes="CHWP - High Eff. Motor")
    line_item1_2_2 = QuoteLineItem(option_id=option1_2.id, product_id=custom_product.id, quantity=12, unit_price=150.00, display_order=2, notes="Premium labour")
    db.session.add_all([line_item1_2_1, line_item1_2_2])
    db.session.commit()
    
    # --- Create Revision 2 for Deal 1 ---
    quote_rev2 = Quote(recipient_id=recipient1.id, revision=2, notes="Revised proposal with cost-saving measures.")
    db.session.add(quote_rev2)
    db.session.commit()

    # Option 1: Revised Standard Offer
    option2_1 = QuoteOption(quote_id=quote_rev2.id, name="Revised Standard Offer", freight_charge=450.00)
    db.session.add(option2_1)
    db.session.commit()
    line_item2_1_1 = QuoteLineItem(option_id=option2_1.id, product_id=product1.id, quantity=2, unit_price=2400.00, discount=5.0, display_order=1, notes="CHWP")
    db.session.add(line_item2_1_1)
    db.session.commit()
    
    logger.info("Database seeding process completed successfully.")

# This allows running the seed script standalone, but using the CLI command is preferred
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()