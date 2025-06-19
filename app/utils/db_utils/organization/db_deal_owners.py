# app/utils/db_utils/organization/db_deal_owners.py

from typing import Dict, List, Optional
import logging
from datetime import datetime
import re
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DealOwnerManager:
    """Manages deal owners within the organization"""

    @staticmethod
    def create_deal_owners_table() -> None:
        """Creates deal owners table"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS deal_owners (
                    id SERIAL PRIMARY KEY,
                    owner_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone_number TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_owner_email UNIQUE (email)
                );
                
                CREATE INDEX IF NOT EXISTS idx_deal_owners_name 
                ON deal_owners(owner_name);
                
                CREATE INDEX IF NOT EXISTS idx_deal_owners_email 
                ON deal_owners(email);
            """
            DatabaseManager.execute_query(query)
            logger.info("Deal owners table created successfully")
        except Exception as e:
            logger.error(f"Error creating deal owners table: {str(e)}")
            raise DatabaseError(f"Failed to create deal owners table: {str(e)}")

    @staticmethod
    def validate_deal_owner_data(data: Dict) -> None:
        """Validate deal owner data before insertion/update"""
        if not data.get('owner_name'):
            raise ValueError("Owner name is required")

        if not data.get('email'):
            raise ValueError("Email is required")

        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            raise ValueError("Invalid email format")

        # Phone number validation (if provided)
        if phone := data.get('phone_number'):
            # Remove common separators for standardization
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not phone.isdigit():
                raise ValueError("Invalid phone number format")
            data['phone_number'] = phone

    @staticmethod
    def insert_deal_owner(owner_data: Dict) -> int:
        """Insert a new deal owner"""
        try:
            # Validate data
            DealOwnerManager.validate_deal_owner_data(owner_data)

            # Check for existing email
            if DatabaseManager.record_exists('deal_owners', {'email': owner_data['email']}):
                raise DatabaseError(f"Deal owner with email {owner_data['email']} already exists")

            fields = ', '.join(owner_data.keys())
            placeholders = ', '.join(['%s'] * len(owner_data))
            query = f"""
                INSERT INTO deal_owners ({fields})
                VALUES ({placeholders})
                RETURNING id
            """
            
            return DatabaseManager.insert_returning_id(query, tuple(owner_data.values()))

        except Exception as e:
            logger.error(f"Error inserting deal owner: {str(e)}")
            raise DatabaseError(f"Failed to insert deal owner: {str(e)}")

    @staticmethod
    def fetch_all_deal_owners() -> List[Dict]:
        """Fetch all deal owners"""
        try:
            query = """
                SELECT 
                    d.*,
                    (SELECT COUNT(*) FROM deals WHERE owner = d.id) as active_deals
                FROM deal_owners d
                ORDER BY owner_name
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching deal owners: {str(e)}")
            raise DatabaseError(f"Failed to fetch deal owners: {str(e)}")

    @staticmethod
    def fetch_deal_owner_by_id(owner_id: int) -> Optional[Dict]:
        """Fetch a specific deal owner by ID"""
        try:
            query = """
                SELECT 
                    d.*,
                    (SELECT COUNT(*) FROM deals WHERE owner = d.id) as active_deals
                FROM deal_owners d
                WHERE d.id = %s
            """
            results = DatabaseManager.execute_query(query, (owner_id,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching deal owner: {str(e)}")
            raise DatabaseError(f"Failed to fetch deal owner: {str(e)}")

    @staticmethod
    def update_deal_owner(owner_id: int, data: Dict) -> None:
        """Update an existing deal owner"""
        try:
            # Get existing owner data
            existing_owner = DealOwnerManager.fetch_deal_owner_by_id(owner_id)
            if not existing_owner:
                raise DatabaseError(f"Deal owner {owner_id} not found")

            # Validate updated data
            if 'email' in data or 'phone_number' in data:
                DealOwnerManager.validate_deal_owner_data({
                    **existing_owner,
                    **data
                })

            fields = [f"{k} = %s" for k in data.keys()]
            query = f"""
                UPDATE deal_owners 
                SET {', '.join(fields)}
                WHERE id = %s
            """
            values = list(data.values()) + [owner_id]
            DatabaseManager.execute_query(query, tuple(values))

        except Exception as e:
            logger.error(f"Error updating deal owner: {str(e)}")
            raise DatabaseError(f"Failed to update deal owner: {str(e)}")

# Initialize table when module is imported
try:
    DealOwnerManager.create_deal_owners_table()
except Exception as e:
    logger.error(f"Failed to initialize deal owners table: {str(e)}")