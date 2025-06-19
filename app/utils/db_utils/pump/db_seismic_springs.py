# app/utils/db_utils/db_seismic_springs.py

from typing import Dict, List, Optional
import logging
from datetime import datetime
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeismicSpringDatabaseManager:
    """Manages all seismic spring-related database operations"""

    @staticmethod
    def create_seismic_springs_table() -> None:
        """Creates seismic springs table with PostgreSQL optimizations"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS seismic_springs (
                    part_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    max_load_kg DECIMAL(10, 2) NOT NULL,
                    static_deflection DECIMAL(10, 3) NOT NULL,
                    spring_constant_kg_mm DECIMAL(10, 3) NOT NULL,
                    stripe1 TEXT,
                    stripe2 TEXT,
                    cost DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT positive_load CHECK (max_load_kg > 0),
                    CONSTRAINT positive_deflection CHECK (static_deflection > 0),
                    CONSTRAINT positive_spring_constant CHECK (spring_constant_kg_mm > 0)
                );

                CREATE INDEX IF NOT EXISTS idx_springs_load 
                ON seismic_springs(max_load_kg);
                
                CREATE INDEX IF NOT EXISTS idx_springs_deflection 
                ON seismic_springs(static_deflection);
            """

            DatabaseManager.execute_query(query)
            logger.info("Seismic springs table created successfully")
        except Exception as e:
            logger.error(f"Error creating seismic springs table: {str(e)}")
            raise DatabaseError(f"Failed to create seismic springs table: {str(e)}")

    @staticmethod
    def validate_seismic_spring_data(data: Dict) -> None:
        """Validate seismic spring data before insertion/update"""
        required_fields = [
            'part_number', 'name', 'max_load_kg', 
            'static_deflection', 'spring_constant_kg_mm', 'cost'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric values
        numeric_fields = ['max_load_kg', 'static_deflection', 'spring_constant_kg_mm', 'cost']
        for field in numeric_fields:
            if field in data:
                try:
                    data[field] = Decimal(str(data[field]))
                    if data[field] <= 0:
                        raise ValueError(f"{field} must be positive")
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid numeric value for {field}")

    @staticmethod
    def insert_seismic_spring(data: Dict) -> str:
        """Insert a new seismic spring with validation and audit logging"""
        try:
            # Validate data
            SeismicSpringDatabaseManager.validate_seismic_spring_data(data)

            # Check for existing part number
            if DatabaseManager.record_exists('seismic_springs', {'part_number': data['part_number']}):
                raise DatabaseError(f"Seismic spring with part number {data['part_number']} already exists")

            # Add timestamps
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO seismic_springs ({fields})
                VALUES ({placeholders})
                RETURNING part_number
            """
            
            result = DatabaseManager.execute_query(query, tuple(data.values()))
            return result[0]['part_number']

        except Exception as e:
            logger.error(f"Error inserting seismic spring: {str(e)}")
            raise DatabaseError(f"Failed to insert seismic spring: {str(e)}")

    @staticmethod
    def fetch_all_seismic_springs() -> List[Dict]:
        """Fetch all seismic springs"""
        try:
            query = """
                SELECT *
                FROM seismic_springs
                ORDER BY part_number
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching seismic springs: {str(e)}")
            raise DatabaseError(f"Failed to fetch seismic springs: {str(e)}")

    @staticmethod
    def fetch_seismic_spring_by_part_number(part_number: str) -> Optional[Dict]:
        """Fetch a specific seismic spring by part number"""
        try:
            query = """
                SELECT * 
                FROM seismic_springs 
                WHERE part_number = %s
            """
            results = DatabaseManager.execute_query(query, (part_number,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching seismic spring: {str(e)}")
            raise DatabaseError(f"Failed to fetch seismic spring: {str(e)}")

# Initialize table when module is imported
try:
    SeismicSpringDatabaseManager.create_seismic_springs_table()
except Exception as e:
    logger.error(f"Failed to initialize seismic springs table: {str(e)}")