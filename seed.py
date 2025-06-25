import random
import inspect
from app import create_app
from app.extensions import db
from app.models import (
    User, Company, Contact, Deal, QuoteRecipient, Quote, QuoteOption, QuoteLineItem,
    DealStage, DealType, AustralianState, UserRole, Product
)

def seed_database():
    """Seeds the database with data reflecting the new Product Catalog model."""
    app = create_app()
    with app.app_context():

        print("\n--- DEBUGGING QuoteLineItem ---")
        print(f"File location: {inspect.getfile(QuoteLineItem)}")
        print(f"Class attributes: {[attr for attr in dir(QuoteLineItem) if not attr.startswith('_')]}")
        print("-----------------------------\n")


        print("Starting database seed with new data model...")

        # Clear existing data in reverse order of dependencies
        print("Clearing old data...")
        db.session.query(QuoteLineItem).delete()
        db.session.query(QuoteOption).delete()
        db.session.query(Quote).delete()
        db.session.query(QuoteRecipient).delete()
        
        # Manually delete from association tables before deleting parent tables
        db.session.execute(db.text('DELETE FROM deal_companies'))
        db.session.execute(db.text('DELETE FROM deal_contacts'))
        
        db.session.query(Deal).delete()
        db.session.query(Contact).delete()
        db.session.query(Company).delete()
        db.session.query(User).delete()
        db.session.query(Product).delete() # Clear products
        db.session.commit()
        print("Old data cleared.")

        # --- Create Sample Users ---
        print("Creating sample users...")
        users_data = [
            {'username': 'Owen', 'email': 'owen@example.com', 'role': UserRole.ADMIN, 'password': 'password123'},
            {'username': 'Jane Smith', 'email': 'jane.smith@example.com', 'role': UserRole.MANAGER, 'password': 'password123'},
            {'username': 'John Doe', 'email': 'john.doe@example.com', 'role': UserRole.SALES, 'password': 'password123'}
        ]
        users = [User(**data) for data in users_data]
        db.session.add_all(users)
        db.session.commit()
        print(f"Created {len(users)} users.")

        # --- Create Sample Companies ---
        print("Creating sample companies...")
        companies_data = [
            {'company_name': 'ACME Mechanical', 'address': '123 HVAC Way, Sydney, NSW'},
            {'company_name': 'Total Flow Plumbing', 'address': '456 Drainpipe Rd, Melbourne, VIC'},
            {'company_name': 'Climate Control Solutions', 'address': '789 Celsius Ct, Brisbane, QLD'}
        ]
        companies = [Company(**data) for data in companies_data]
        db.session.add_all(companies)
        db.session.commit()
        print(f"Created {len(companies)} companies.")

        # --- Create Sample Contacts ---
        print("Creating sample contacts...")
        contacts_data = [
            {'name': 'Alice Innovate', 'email': 'alice@acme.com', 'company_id': companies[0].id},
            {'name': 'Bob Builder', 'email': 'bob@totalflow.com', 'company_id': companies[1].id},
            {'name': 'Charlie Climate', 'email': 'charlie@climate.com', 'company_id': companies[2].id}
        ]
        contacts = [Contact(**data) for data in contacts_data]
        db.session.add_all(contacts)
        db.session.commit()
        print(f"Created {len(contacts)} contacts.")
        
        # --- Create Sample Products ---
        print("Creating sample products...")
        products_data = [
            {'sku': 'PMP-1001', 'name': 'Centrifugal Pump - Model A', 'description': 'Standard duty centrifugal pump.', 'unit_price': 1250.00},
            {'sku': 'PMP-1002', 'name': 'Centrifugal Pump - Model B', 'description': 'Heavy duty centrifugal pump.', 'unit_price': 2500.00},
            {'sku': 'SEP-2001', 'name': 'Air & Dirt Separator - 50mm', 'description': 'Standard separator.', 'unit_price': 350.00},
            {'sku': 'VAL-3001', 'name': 'Butterfly Valve - 80mm', 'description': 'Standard butterfly valve.', 'unit_price': 120.00},
            {'sku': 'CUSTOM', 'name': 'Custom Labour Charge', 'description': 'Hourly rate for custom work.', 'unit_price': 150.00}
        ]
        products = [Product(**data) for data in products_data]
        db.session.add_all(products)
        db.session.commit()
        print(f"Created {len(products)} products.")

        # --- Create Sample Deals and all child objects ---
        print("Creating sample deals, quote streams, quotes, options, and line items...")
        for i in range(10): # Create 10 deals
            deal_owner = random.choice(users)
            
            # Use a set to automatically prevent duplicate company associations
            deal_companies_set = set(random.sample(companies, k=random.randint(1, 2)))
            selected_contact = random.choice(contacts)
            # Add the selected contact's company to the set. Duplicates are ignored.
            if selected_contact.company:
                deal_companies_set.add(selected_contact.company)

            deal = Deal(
                project_name=f'Project Alpha-{i+1}',
                owner_id=deal_owner.id,
                stage=random.choice(list(DealStage)),
                deal_type=random.choice(list(DealType)),
                state=random.choice(list(AustralianState))
            )
            
            # Associate the unique companies and the contact
            deal.companies.extend(list(deal_companies_set))
            deal.contacts.append(selected_contact)
            
            db.session.add(deal)
            db.session.flush()

            # For each company in the deal, create a QuoteRecipient stream
            for company in deal.companies:
                recipient = QuoteRecipient(deal_id=deal.id, company_id=company.id)
                db.session.add(recipient)
                db.session.flush()

                # Create 1 to 3 quote revisions for this company's stream
                for rev_num in range(1, random.randint(2, 4)):
                    quote = Quote(recipient_id=recipient.id, revision=rev_num, notes=f"Notes for Rev {rev_num}")
                    db.session.add(quote)
                    db.session.flush()
                    
                    # Create 1 to 2 options within this quote revision
                    for opt_num in range(1, random.randint(2, 3)):
                        option = QuoteOption(quote_id=quote.id, name=f'Option {chr(65+opt_num-1)}')
                        db.session.add(option)
                        db.session.flush()

                        # Create line items for this option linked to products
                        for _ in range(random.randint(2, 5)):
                            product = random.choice(products)
                            line_item = QuoteLineItem(
                                option_id=option.id,
                                product_id=product.id,
                                quantity=random.randint(1, 5),
                                unit_price=product.unit_price, # Start with the default price
                                notes="CHWP" if "Pump" in product.name else "General"
                            )
                            db.session.add(line_item)
        
        db.session.commit()
        print("Database seeding complete!")

if __name__ == '__main__':
    seed_database()