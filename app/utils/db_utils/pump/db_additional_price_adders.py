# app/utils/db_utils/db_additional_price_adders.py

from typing import Dict, List, Optional
import logging
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdditionalPriceAdderManager:
    """Manages all additional price adder operations"""

    @staticmethod
    def create_additional_price_adders_table() -> None:
        """Creates additional price adders table with PostgreSQL optimizations"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS additional_price_adders (
                    id SERIAL PRIMARY KEY,
                    ip_adder DECIMAL(10, 2) NOT NULL,
                    drip_tray_adder DECIMAL(10, 2) NOT NULL,
                    CONSTRAINT positive_ip_adder CHECK (ip_adder >= 0),
                    CONSTRAINT positive_drip_tray_adder CHECK (drip_tray_adder >= 0)
                )
            """
            
            DatabaseManager.execute_query(query)
            logger.info("Additional price adders table created successfully")
        except Exception as e:
            logger.error(f"Error creating additional price adders table: {str(e)}")
            raise DatabaseError(f"Failed to create additional price adders table: {str(e)}")

    @staticmethod
    def validate_adder_data(data: Dict) -> None:
        """Validate price adder data before insertion/update"""
        required_fields = ['ip_adder', 'drip_tray_adder']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric values
        for field in required_fields:
            try:
                data[field] = Decimal(str(data[field]))
                if data[field] < 0:
                    raise ValueError(f"{field} cannot be negative")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numeric value for {field}")

    @staticmethod
    def insert_additional_price_adder(data: Dict) -> int:
        """Insert a new additional price adder record"""
        try:
            # Validate data
            AdditionalPriceAdderManager.validate_adder_data(data)

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO additional_price_adders ({fields})
                VALUES ({placeholders})
                RETURNING id
            """
            
            return DatabaseManager.insert_returning_id(query, tuple(data.values()))

        except Exception as e:
            logger.error(f"Error inserting additional price adder: {str(e)}")
            raise DatabaseError(f"Failed to insert additional price adder: {str(e)}")

    @staticmethod
    def fetch_all_additional_price_adders() -> List[Dict]:
        """Fetch all additional price adders"""
        try:
            query = """
                SELECT *
                FROM additional_price_adders
                ORDER BY id
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching additional price adders: {str(e)}")
            raise DatabaseError(f"Failed to fetch additional price adders: {str(e)}")

    @staticmethod
    def fetch_adder_by_id(adder_id: int) -> Optional[Dict]:
        """Fetch a specific additional price adder by id"""
        try:
            query = """
                SELECT * 
                FROM additional_price_adders 
                WHERE id = %s
            """
            results = DatabaseManager.execute_query(query, (adder_id,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching additional price adder: {str(e)}")
            raise DatabaseError(f"Failed to fetch additional price adder: {str(e)}")

    @staticmethod
    def update_adder(adder_id: int, data: Dict) -> None:
        """Update an existing additional price adder"""
        try:
            # Validate update data
            AdditionalPriceAdderManager.validate_adder_data(data)

            fields = [f"{k} = %s" for k in data.keys()]
            query = f"""
                UPDATE additional_price_adders 
                SET {', '.join(fields)}
                WHERE id = %s
            """
            values = list(data.values()) + [adder_id]
            DatabaseManager.execute_query(query, tuple(values))

        except Exception as e:
            logger.error(f"Error updating additional price adder: {str(e)}")
            raise DatabaseError(f"Failed to update additional price adder: {str(e)}")

# Initialize table when module is imported
try:
    AdditionalPriceAdderManager.create_additional_price_adders_table()
except Exception as e:
    logger.error(f"Failed to initialize additional price adders table: {str(e)}")