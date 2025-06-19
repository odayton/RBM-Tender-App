# app/utils/db_utils/db_contacts.py

from typing import Dict, List, Optional
import logging
import re
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactDatabaseManager:
    """Handles all contact-related database operations"""

    @staticmethod
    def create_contact_tables() -> None:
        """Creates contact-related tables with PostgreSQL optimizations"""
        try:
            queries = [
                # Contacts table
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    representative_name TEXT NOT NULL,
                    representative_email TEXT NOT NULL,
                    phone_number TEXT,
                    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
                    CONSTRAINT unique_email_per_company UNIQUE (representative_email, company_id)
                );

                CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
                CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(representative_email);
                """,

                # Deal Contacts junction table
                """
                CREATE TABLE IF NOT EXISTS deal_contacts (
                    id SERIAL PRIMARY KEY,
                    deal_id INTEGER REFERENCES deals(id) ON DELETE CASCADE,
                    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
                    UNIQUE (deal_id, contact_id)
                );

                CREATE INDEX IF NOT EXISTS idx_deal_contacts ON deal_contacts(deal_id, contact_id);
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)

            logger.info("Contact tables created successfully")
        except Exception as e:
            logger.error(f"Error creating contact tables: {str(e)}")
            raise DatabaseError(f"Failed to create contact tables: {str(e)}")

    @staticmethod
    def validate_contact_data(contact_data: Dict) -> None:
        """Validate contact data before insertion/update"""
        if not contact_data.get('representative_name'):
            raise ValueError("Representative name is required")
        
        email = contact_data.get('representative_email')
        if not email:
            raise ValueError("Email is required")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        # Phone number validation (if provided)
        phone = contact_data.get('phone_number')
        if phone:
            # Remove common separators for standardization
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not phone.isdigit():
                raise ValueError("Invalid phone number format")
            contact_data['phone_number'] = phone

    @staticmethod
    def insert_contact(contact_data: Dict) -> int:
        """Insert a new contact with validation"""
        try:
            # Validate contact data
            ContactDatabaseManager.validate_contact_data(contact_data)

            # Check for existing contact with same email in same company
            if DatabaseManager.record_exists(
                'contacts', 
                {
                    'representative_email': contact_data['representative_email'],
                    'company_id': contact_data.get('company_id')
                }
            ):
                raise DatabaseError("Contact with this email already exists for this company")

            fields = ', '.join(contact_data.keys())
            placeholders = ', '.join(['%s'] * len(contact_data))
            query = f"""
                INSERT INTO contacts ({fields})
                VALUES ({placeholders})
                RETURNING id
            """
            
            return DatabaseManager.insert_returning_id(query, tuple(contact_data.values()))

        except Exception as e:
            logger.error(f"Error inserting contact: {str(e)}")
            raise DatabaseError(f"Failed to insert contact: {str(e)}")

    @staticmethod
    def fetch_all_contacts() -> List[Dict]:
        """Fetch all contacts with company information"""
        try:
            query = """
                SELECT 
                    c.*,
                    comp.company_name
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id
                ORDER BY c.representative_name
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching contacts: {str(e)}")
            raise DatabaseError(f"Failed to fetch contacts: {str(e)}")

    @staticmethod
    def add_contact_to_deal(deal_id: int, contact_id: int) -> None:
        """Add a contact to a deal"""
        try:
            query = """
                INSERT INTO deal_contacts (deal_id, contact_id)
                VALUES (%s, %s)
                ON CONFLICT (deal_id, contact_id) DO NOTHING
            """
            DatabaseManager.execute_query(query, (deal_id, contact_id))

        except Exception as e:
            logger.error(f"Error adding contact to deal: {str(e)}")
            raise DatabaseError(f"Failed to add contact to deal: {str(e)}")

    @staticmethod
    def update_contact(contact_id: int, updated_data: Dict) -> None:
        """Update contact information with validation"""
        try:
            # Get existing contact data
            existing_contact = ContactDatabaseManager.fetch_contact_by_id(contact_id)
            if not existing_contact:
                raise DatabaseError(f"Contact {contact_id} not found")

            # Validate updated data
            if 'representative_email' in updated_data or 'phone_number' in updated_data:
                ContactDatabaseManager.validate_contact_data({
                    **existing_contact,
                    **updated_data
                })

            fields = [f"{k} = %s" for k in updated_data.keys()]
            query = f"""
                UPDATE contacts 
                SET {', '.join(fields)}
                WHERE id = %s
            """
            values = list(updated_data.values()) + [contact_id]
            DatabaseManager.execute_query(query, tuple(values))

        except Exception as e:
            logger.error(f"Error updating contact: {str(e)}")
            raise DatabaseError(f"Failed to update contact: {str(e)}")

    @staticmethod
    def fetch_contact_by_id(contact_id: int) -> Optional[Dict]:
        """Fetch a specific contact with company information"""
        try:
            query = """
                SELECT 
                    c.*,
                    comp.company_name
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id
                WHERE c.id = %s
            """
            results = DatabaseManager.execute_query(query, (contact_id,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching contact: {str(e)}")
            raise DatabaseError(f"Failed to fetch contact: {str(e)}")

# Initialize tables when module is imported
try:
    ContactDatabaseManager.create_contact_tables()
except Exception as e:
    logger.error(f"Failed to initialize contact tables: {str(e)}")