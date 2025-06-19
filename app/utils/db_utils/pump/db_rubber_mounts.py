# app/utils/db_utils/db_rubber_mounts.py

from typing import Dict, List, Optional
import logging
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RubberMountDatabaseManager:
    """Manages all rubber mount-related database operations"""

    @staticmethod
    def create_rubber_mounts_table() -> None:
        """Creates rubber mounts table with PostgreSQL optimizations"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS rubber_mounts (
                    part_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    weight DECIMAL(10, 2) NOT NULL,
                    cost DECIMAL(10, 2) NOT NULL,
                    CONSTRAINT positive_weight CHECK (weight > 0),
                    CONSTRAINT positive_cost CHECK (cost > 0)
                );

                CREATE INDEX IF NOT EXISTS idx_rubber_mounts_weight 
                ON rubber_mounts(weight);
            """

            DatabaseManager.execute_query(query)
            logger.info("Rubber mounts table created successfully")
        except Exception as e:
            logger.error(f"Error creating rubber mounts table: {str(e)}")
            raise DatabaseError(f"Failed to create rubber mounts table: {str(e)}")

    @staticmethod
    def validate_rubber_mount_data(data: Dict) -> None:
        """Validate rubber mount data before insertion/update"""
        required_fields = ['part_number', 'name', 'weight', 'cost']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric values
        numeric_fields = ['weight', 'cost']
        for field in numeric_fields:
            if field in data:
                try:
                    data[field] = Decimal(str(data[field]))
                    if data[field] <= 0:
                        raise ValueError(f"{field} must be positive")
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid numeric value for {field}")

    @staticmethod
    def insert_rubber_mount(data: Dict) -> str:
        """Insert a new rubber mount with validation"""
        try:
            # Validate data
            RubberMountDatabaseManager.validate_rubber_mount_data(data)

            # Check for existing part number
            if DatabaseManager.record_exists('rubber_mounts', {'part_number': data['part_number']}):
                raise DatabaseError(f"Rubber mount with part number {data['part_number']} already exists")

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO rubber_mounts ({fields})
                VALUES ({placeholders})
                RETURNING part_number
            """
            
            result = DatabaseManager.execute_query(query, tuple(data.values()))
            return result[0]['part_number']

        except Exception as e:
            logger.error(f"Error inserting rubber mount: {str(e)}")
            raise DatabaseError(f"Failed to insert rubber mount: {str(e)}")

    @staticmethod
    def fetch_all_rubber_mounts() -> List[Dict]:
        """Fetch all rubber mounts"""
        try:
            query = """
                SELECT *
                FROM rubber_mounts
                ORDER BY part_number
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching rubber mounts: {str(e)}")
            raise DatabaseError(f"Failed to fetch rubber mounts: {str(e)}")

    @staticmethod
    def fetch_rubber_mount_by_part_number(part_number: str) -> Optional[Dict]:
        """Fetch a specific rubber mount by part number"""
        try:
            query = """
                SELECT * 
                FROM rubber_mounts 
                WHERE part_number = %s
            """
            results = DatabaseManager.execute_query(query, (part_number,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching rubber mount: {str(e)}")
            raise DatabaseError(f"Failed to fetch rubber mount: {str(e)}")

# Initialize table when module is imported
try:
    RubberMountDatabaseManager.create_rubber_mounts_table()
except Exception as e:
    logger.error(f"Failed to initialize rubber mounts table: {str(e)}")