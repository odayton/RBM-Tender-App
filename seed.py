import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    User, Company, Contact, Deal, Quote, QuoteLineItem,
    DealStage, DealType, AustralianState
)
# Note: UserRole is part of User model, not a separate import usually
from app.models.user_model import UserRole


def seed_database():
    """Seeds the database with more relevant sample data."""
    app = create_app()
    with app.app_context():
        print("Starting database seed...")

        # Clear existing data in reverse order of dependencies
        print("Clearing old data...")
        QuoteLineItem.query.delete()
        # The new association tables will be cleared automatically by SQLAlchemy
        # when the parent objects are deleted due to the cascade settings.
        Quote.query.delete()
        Deal.query.delete()
        Contact.query.delete()
        Company.query.delete()
        User.query.delete()
        db.session.commit()
        print("Old data cleared.")

        # --- Create Sample Users (Deal Owners) ---
        print("Creating sample users...")
        users_data = [
            {'username': 'Owen', 'email': 'owen@example.com', 'role': UserRole.ADMIN},
            {'username': 'Jane Smith', 'email': 'jane.smith@example.com', 'role': UserRole.MANAGER},
            {'username': 'John Doe', 'email': 'john.doe@example.com', 'role': UserRole.SALES},
        ]
        users = []
        for user_data in users_data:
            user = User(username=user_data['username'], email=user_data['email'], role=user_data['role'])
            
            # --- THIS IS THE FIX ---
            # Assign the password directly to the attribute
            user.password = 'password123'
            # ---------------------

            users.append(user)
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users.")

        # --- Create Sample Companies ---
        print("Creating sample companies...")
        companies_data = [
            {'company_name': 'ACME Mechanical', 'address': '123 HVAC Way, Sydney, NSW'},
            {'company_name': 'Total Flow Plumbing', 'address': '456 Drainpipe Rd, Melbourne, VIC'},
            {'company_name': 'Climate Control Solutions', 'address': '789 Celsius Ct, Brisbane, QLD'},
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
            {'name': 'Charlie Climate', 'email': 'charlie@climate.com', 'company_id': companies[2].id},
            {'name': 'Diana Drake', 'email': 'diana@acme.com', 'company_id': companies[0].id},
        ]
        contacts = [Contact(**data) for data in contacts_data]
        db.session.add_all(contacts)
        db.session.commit()
        print(f"Created {len(contacts)} contacts.")

        # --- Create Sample Deals, Quotes, and Line Items ---
        print("Creating sample deals and quotes...")
        for i in range(15):
            # 1. Create the Deal object first
            deal_owner = random.choice(users)
            deal = Deal(
                project_name=f'{random.choice(["City Tower", "Westfield Mall", "St. Marys Hospital", "Metro Station"])} - {random.choice(["HVAC Upgrade", "Plumbing Fitout", "Data Center Cooling"])} {i+1}',
                state=random.choice(list(AustralianState)),
                deal_type=random.choice(list(DealType)),
                stage=random.choice(list(DealStage)),
                owner_id=deal_owner.id
            )

            # 2. Append companies and contacts using the many-to-many relationship
            deal.companies.append(random.choice(companies))
            deal.contacts.append(random.choice(contacts))
            # Sometimes add a second contact
            if i % 3 == 0:
                deal.contacts.append(random.choice([c for c in contacts if c not in deal.contacts]))

            db.session.add(deal)
            db.session.flush() # Flush to get the deal ID for the quote

            # 3. Create a Quote for the Deal
            quote = Quote(
                deal_id=deal.id,
                revision=1
            )
            # Assign a specific contact from the deal to this quote revision
            quote.contacts.append(random.choice(deal.contacts))
            db.session.add(quote)
            db.session.flush() # Flush to get the quote ID for line items

            # 4. Create Line Items for the Quote
            total_quote_amount = 0
            for j in range(random.randint(1, 4)): # Add 1 to 4 line items
                price = random.randint(500, 20000)
                qty = random.randint(1, 3)
                line_item = QuoteLineItem(
                    quote_id=quote.id,
                    description=f'Pump Model {random.choice(["A", "B", "C"])}-{random.randint(100,999)}',
                    quantity=qty,
                    unit_price=price
                )
                total_quote_amount += (price * qty)
                db.session.add(line_item)
            
            # 5. Update the deal's total amount based on the quote
            deal.total_amount = total_quote_amount

        db.session.commit()
        print(f"Created 15 deals with associated quotes and line items.")

        print("Database seeding complete!")

if __name__ == '__main__':
    seed_database()