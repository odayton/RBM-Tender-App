from typing import Dict, List, Optional
import logging
from datetime import datetime
from app.core.core_database import DatabaseManager
from app.core.core_errors import DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PumpDatabaseManager:
    """Handles all pump-related database operations"""

    @staticmethod
    def create_pump_tables() -> None:
        """Creates tables related to pump details with PostgreSQL optimizations"""
        try:
            queries = [
                # General Pump Details table
                """
                CREATE TABLE IF NOT EXISTS general_pump_details (
                    sku TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    poles INTEGER,
                    kw DECIMAL(10, 2),
                    ie_class TEXT,
                    mei DECIMAL(10, 3),
                    weight DECIMAL(10, 2),
                    length DECIMAL(10, 2),
                    width DECIMAL(10, 2),
                    height DECIMAL(10, 2),
                    image_path TEXT,
                    list_price DECIMAL(10, 2)
                );
                
                CREATE INDEX IF NOT EXISTS idx_pump_name ON general_pump_details (name);
                CREATE INDEX IF NOT EXISTS idx_pump_kw ON general_pump_details (kw);
                """,
                
                # Historic Pump Data table
                """
                CREATE TABLE IF NOT EXISTS historic_pump_data (
                    sku TEXT NOT NULL REFERENCES general_pump_details(sku) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    flow DECIMAL(10, 2),
                    flow_unit TEXT,
                    head DECIMAL(10, 2),
                    head_unit TEXT,
                    efficiency TEXT,
                    absorbed_power TEXT,
                    npsh TEXT,
                    image_path TEXT,
                    CONSTRAINT unique_historic_data UNIQUE (sku, flow, head)
                );
                
                CREATE INDEX IF NOT EXISTS idx_historic_sku ON historic_pump_data (sku);
                CREATE INDEX IF NOT EXISTS idx_historic_flow_head ON historic_pump_data (flow, head);
                """
            ]
            
            for query in queries:
                DatabaseManager.execute_query(query)
            
            logger.info("Pump tables created successfully")
        except Exception as e:
            logger.error(f"Error creating pump tables: {str(e)}")
            raise DatabaseError(f"Failed to create pump tables: {str(e)}")

    @staticmethod
    def insert_general_pump_details(pump_data: Dict) -> None:
        """Insert or update general pump details"""
        try:
            # Check if pump exists
            existing_pump = PumpDatabaseManager.fetch_pump_by_sku(pump_data['sku'])
            
            if existing_pump:
                # Update existing pump
                fields = [f"{k} = %s" for k in pump_data.keys()]
                query = f"""
                    UPDATE general_pump_details 
                    SET {', '.join(fields)}
                    WHERE sku = %s
                """
                values = list(pump_data.values()) + [pump_data['sku']]
                DatabaseManager.execute_query(query, tuple(values))
                logger.info(f"Updated pump with SKU: {pump_data['sku']}")
            else:
                # Insert new pump
                fields = ', '.join(pump_data.keys())
                placeholders = ', '.join(['%s'] * len(pump_data))
                query = f"""
                    INSERT INTO general_pump_details ({fields})
                    VALUES ({placeholders})
                """
                DatabaseManager.execute_query(query, tuple(pump_data.values()))
                logger.info(f"Inserted new pump with SKU: {pump_data['sku']}")

        except Exception as e:
            logger.error(f"Error inserting/updating pump details: {str(e)}")
            raise DatabaseError(f"Failed to insert/update pump: {str(e)}")

    @staticmethod
    def fetch_all_general_pumps() -> List[Dict]:
        """Fetch all records from general_pump_details"""
        try:
            query = """
                SELECT * FROM general_pump_details
                ORDER BY sku
            """
            return DatabaseManager.execute_query(query)
        except Exception as e:
            logger.error(f"Error fetching all pumps: {str(e)}")
            raise DatabaseError(f"Failed to fetch pumps: {str(e)}")

    @staticmethod
    def fetch_pump_by_sku(sku: str) -> Optional[Dict]:
        """Fetch a specific pump by SKU"""
        try:
            query = "SELECT * FROM general_pump_details WHERE sku = %s"
            results = DatabaseManager.execute_query(query, (sku,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching pump by SKU: {str(e)}")
            raise DatabaseError(f"Failed to fetch pump: {str(e)}")

    @staticmethod
    def fetch_historic_pump_data() -> List[Dict]:
        """Fetch all historic pump data"""
        try:
            query = """
                SELECT h.*, g.poles, g.kw
                FROM historic_pump_data h
                LEFT JOIN general_pump_details g ON h.sku = g.sku
                ORDER BY h.sku
            """
            return DatabaseManager.execute_query(query)
        except Exception as e:
            logger.error(f"Error fetching historic pump data: {str(e)}")
            raise DatabaseError(f"Failed to fetch historic data: {str(e)}")

    @staticmethod
    def insert_historic_pump_data(data: Dict) -> None:
        """Insert historic pump data"""
        try:
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO historic_pump_data ({fields})
                VALUES ({placeholders})
                ON CONFLICT (sku, flow, head) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    flow_unit = EXCLUDED.flow_unit,
                    head_unit = EXCLUDED.head_unit,
                    efficiency = EXCLUDED.efficiency,
                    absorbed_power = EXCLUDED.absorbed_power,
                    npsh = EXCLUDED.npsh,
                    image_path = EXCLUDED.image_path
            """
            DatabaseManager.execute_query(query, tuple(data.values()))
            logger.info(f"Inserted/Updated historic data for SKU: {data['sku']}")
        except Exception as e:
            logger.error(f"Error inserting historic pump data: {str(e)}")
            raise DatabaseError(f"Failed to insert historic data: {str(e)}")

# Initialize tables when module is imported
try:
    PumpDatabaseManager.create_pump_tables()
except Exception as e:
    logger.error(f"Failed to initialize pump tables: {str(e)}")