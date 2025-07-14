import logging
import csv
from sqlalchemy import text
from app import create_app
from app.extensions import db
from app.models import (
    User, UserRole, Company, Contact, Product,
    Deal, DealStage, DealType, AustralianState,
    Quote, QuoteRecipient, QuoteOption, QuoteLineItem,
    Pump, PumpAssembly, InertiaBase, SeismicSpring, RubberMount,
    Discount
)

logger = logging.getLogger(__name__)

def seed_discounts():
    """Seeds the discounts table from a CSV file."""
    logger.info("--- Starting discount seeding ---")
    try:
        with open('data/discounts.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                disc_code = row.get('Disc Code')
                if not disc_code: continue
                amount_str = row.get('Amount', '0').strip().replace('%', '')
                amount = float(amount_str)
                if not Discount.query.filter_by(code=disc_code).first():
                    db.session.add(Discount(code=disc_code, percentage=amount))
        db.session.commit()
        logger.info("--- Discounts seeded successfully ---")
    except FileNotFoundError:
        logger.error("[ERROR] 'data/discounts.csv' not found. Skipping discount seeding.")
    except Exception as e:
        logger.error(f"[ERROR] An error occurred during discount seeding: {e}")
        db.session.rollback()

def seed_products():
    """Seeds the products table from the main price book CSV."""
    logger.info("--- Starting product seeding ---")
    products_added = 0
    try:
        with open('data/products.csv', mode='r', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            logger.info(f"Found {len(rows)} rows in the CSV file.")
            
            for i, row in enumerate(rows):
                sku = row.get('Item No')
                if not sku or not sku.strip():
                    continue

                try:
                    price_str = row.get('2025 List Price', '0')
                    # --- THE FINAL FIX: Clean the price string ---
                    cleaned_price_str = price_str.replace('$', '').replace(',', '')
                    price = float(cleaned_price_str if cleaned_price_str else 0)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert price '{price_str}' to a number for SKU '{sku}'. Defaulting to 0.")
                    price = 0.0
                
                if not Product.query.filter_by(sku=sku).first():
                    product = Product(
                        sku=sku,
                        name=row.get('Description'),
                        unit_price=price,
                        discount_code=row.get('Disc Code')
                    )
                    db.session.add(product)
                    products_added += 1
        
        db.session.commit()
        logger.info(f"--- Products seeded successfully: {products_added} new products added. ---")

    except FileNotFoundError:
        logger.error("[ERROR] 'data/products.csv' not found.")
    except Exception as e:
        logger.error(f"[ERROR] An error occurred during product seeding: {e}")
        db.session.rollback()


def seed_database():
    """Seeds the database with initial data in an idempotent way."""
    logger.info(">>> Starting database seeding process <<<")

    logger.info("Clearing existing data...")
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if db.engine.name == 'sqlite':
            db.session.execute(text('PRAGMA foreign_keys=OFF;'))
        else:
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        db.session.execute(table.delete())
        if db.engine.name == 'sqlite':
            db.session.execute(text('PRAGMA foreign_keys=ON;'))
        else:
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
    db.session.commit()
    logger.info("Data cleared.")

    seed_discounts()
    seed_products() 

    logger.info("Seeding sample users and deals...")
    admin_user = User(username='admin', email='admin@example.com', first_name='Admin', last_name='User', role=UserRole.ADMIN, is_active=True)
    admin_user.password = 'password'
    dev_user = User(username='devuser', email='dev@example.com', first_name='Dev', last_name='User', role=UserRole.SALES, is_active=True)
    dev_user.password = 'password'
    db.session.add_all([admin_user, dev_user])
    db.session.commit()
    
    company1 = Company(company_name='ACME Mechanical', address='123 Industrial Way, Sydney NSW')
    db.session.add(company1)
    db.session.commit()

    contact1 = Contact(name='John Smith', email='john.s@acme.com', phone_number='0411222333', company_id=company1.id)
    db.session.add(contact1)
    db.session.commit()
    
    deal1 = Deal(project_name='City Hospital HVAC Upgrade', owner_id=dev_user.id, stage=DealStage.PROPOSAL, deal_type=DealType.HVAC, state=AustralianState.NSW, companies=[company1], contacts=[contact1])
    db.session.add(deal1)
    db.session.commit()

    logger.info(">>> Database seeding process completed successfully. <<<")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()