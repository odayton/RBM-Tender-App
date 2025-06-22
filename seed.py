import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import User, Company, Contact, Deal, DealStage, DealType, AustralianState, UserRole

def seed_database():
    """Seeds the database with sample data."""
    app = create_app()
    with app.app_context():
        print("Starting database seed...")

        # Clear existing data in reverse order of dependencies
        print("Clearing old data...")
        Deal.query.delete()
        Contact.query.delete()
        Company.query.delete()
        User.query.delete()
        db.session.commit()
        print("Old data cleared.")

        # --- Create Sample Users (Deal Owners) ---
        print("Creating sample users...")
        users_data = [
            {'username': 'John Doe', 'email': 'john.doe@example.com', 'role': UserRole.SALES},
            {'username': 'Jane Smith', 'email': 'jane.smith@example.com', 'role': UserRole.MANAGER},
            {'username': 'Peter Jones', 'email': 'peter.jones@example.com', 'role': UserRole.ADMIN},
        ]
        users = []
        for user_data in users_data:
            user = User(**user_data, password='password123') # Set a default password
            users.append(user)
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users.")

        # --- Create Sample Companies ---
        print("Creating sample companies...")
        companies_data = [
            {'company_name': 'Innovate Corp', 'address': '123 Tech Street, Sydney, NSW'},
            {'company_name': 'Builders United', 'address': '456 Construction Ave, Melbourne, VIC'},
            {'company_name': 'Future Solutions', 'address': '789 Future Rd, Brisbane, QLD'},
        ]
        companies = []
        for company_data in companies_data:
            company = Company(**company_data)
            companies.append(company)
            db.session.add(company)
        db.session.commit()
        print(f"Created {len(companies)} companies.")

        # --- Create Sample Contacts ---
        print("Creating sample contacts...")
        contacts_data = [
            {'name': 'Alice', 'email': 'alice@innovate.com', 'company_id': companies[0].id},
            {'name': 'Bob', 'email': 'bob@builders.com', 'company_id': companies[1].id},
            {'name': 'Charlie', 'email': 'charlie@future.com', 'company_id': companies[2].id},
        ]
        for contact_data in contacts_data:
            contact = Contact(**contact_data)
            db.session.add(contact)
        db.session.commit()
        print(f"Created {len(contacts_data)} contacts.")

        # --- Create Sample Deals ---
        print("Creating sample deals...")
        deals_data = []
        for i in range(15): # Create 15 deals
            deal = {
                'project_name': f'Project Alpha {i+1}',
                'state': random.choice(list(AustralianState)),
                'deal_type': random.choice(list(DealType)),
                'stage': random.choice(list(DealStage)),
                'total_amount': random.randint(5000, 150000),
                'created_at': datetime.utcnow() - timedelta(days=random.randint(0, 90)),
                'company_id': random.choice(companies).id,
                'owner_id': random.choice(users).id,
            }
            deals_data.append(deal)

        for deal_data in deals_data:
            deal = Deal(**deal_data)
            db.session.add(deal)
        db.session.commit()
        print(f"Created {len(deals_data)} deals.")

        print("Database seeding complete!")

if __name__ == '__main__':
    seed_database()