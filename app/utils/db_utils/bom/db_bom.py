# app/utils/db_utils/db_bom.py

from typing import Dict, List, Optional
import logging
import pandas as pd
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BOMDatabaseManager:
    """Manages all BOM-related database operations"""

    @staticmethod
    def create_bom_table() -> None:
        """Creates BOM table with PostgreSQL optimizations"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS bom (
                    id SERIAL PRIMARY KEY,
                    pump_sku TEXT NOT NULL,
                    inertia_base_part_number TEXT,
                    seismic_spring_part_number TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pump_sku) REFERENCES general_pump_details(sku),
                    FOREIGN KEY (inertia_base_part_number) REFERENCES inertia_bases(part_number),
                    FOREIGN KEY (seismic_spring_part_number) REFERENCES seismic_springs(part_number)
                );

                CREATE INDEX IF NOT EXISTS idx_bom_pump_sku ON bom(pump_sku);
                CREATE INDEX IF NOT EXISTS idx_bom_inertia_base ON bom(inertia_base_part_number);
                CREATE INDEX IF NOT EXISTS idx_bom_seismic_spring ON bom(seismic_spring_part_number);
            """

            DatabaseManager.execute_query(query)
            logger.info("BOM table created successfully")
        except Exception as e:
            logger.error(f"Error creating BOM table: {str(e)}")
            raise DatabaseError(f"Failed to create BOM table: {str(e)}")

    @staticmethod
    def validate_bom_data(data: Dict) -> None:
        """Validate BOM data before insertion/update"""
        if not data.get('pump_sku'):
            raise ValueError("Pump SKU is required")

    @staticmethod
    def insert_bom_entry(data: Dict) -> None:
        """Insert a new BOM entry with validation"""
        try:
            logger.info(f"Attempting to insert BOM entry with data: {data}")
            
            # Validate data
            BOMDatabaseManager.validate_bom_data(data)

            # Check if entry already exists
            existing_entry = BOMDatabaseManager.get_bom_for_pump(data['pump_sku'])
            
            if existing_entry:
                # Update existing entry
                query = """
                    UPDATE bom 
                    SET inertia_base_part_number = %s,
                        seismic_spring_part_number = %s
                    WHERE pump_sku = %s
                """
                params = (
                    data.get('inertia_base_part_number'),
                    data.get('seismic_spring_part_number'),
                    data['pump_sku']
                )
                DatabaseManager.execute_query(query, params)
                logger.info(f"Updated BOM entry for pump SKU: {data['pump_sku']}")
            else:
                # Insert new entry
                fields = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                query = f"""
                    INSERT INTO bom ({fields})
                    VALUES ({placeholders})
                """
                DatabaseManager.execute_query(query, tuple(data.values()))
                logger.info(f"Inserted new BOM entry for pump SKU: {data['pump_sku']}")

        except Exception as e:
            logger.error(f"Error inserting BOM entry: {str(e)}")
            raise DatabaseError(f"Failed to insert BOM entry: {str(e)}")

    @staticmethod
    def fetch_all_bom_entries() -> List[Dict]:
        """Fetch all BOM entries with related information"""
        try:
            query = """
                SELECT 
                    b.*,
                    g.name as pump_name,
                    i.name as inertia_base_name,
                    s.name as spring_name
                FROM bom b
                LEFT JOIN general_pump_details g ON b.pump_sku = g.sku
                LEFT JOIN inertia_bases i ON b.inertia_base_part_number = i.part_number
                LEFT JOIN seismic_springs s ON b.seismic_spring_part_number = s.part_number
                ORDER BY b.pump_sku
            """
            return DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error fetching BOM entries: {str(e)}")
            raise DatabaseError(f"Failed to fetch BOM entries: {str(e)}")

    @staticmethod
    def get_bom_for_pump(pump_sku: str) -> Optional[Dict]:
        """Get BOM entry for a specific pump"""
        try:
            query = """
                SELECT 
                    b.*,
                    g.name as pump_name,
                    i.name as inertia_base_name,
                    s.name as spring_name
                FROM bom b
                LEFT JOIN general_pump_details g ON b.pump_sku = g.sku
                LEFT JOIN inertia_bases i ON b.inertia_base_part_number = i.part_number
                LEFT JOIN seismic_springs s ON b.seismic_spring_part_number = s.part_number
                WHERE b.pump_sku = %s
            """
            results = DatabaseManager.execute_query(query, (pump_sku,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching BOM for pump: {str(e)}")
            raise DatabaseError(f"Failed to fetch BOM for pump: {str(e)}")

    @staticmethod
    def process_bom_excel(file_path: str, sheet_name: str) -> None:
        """Process BOM data from Excel file"""
        try:
            logger.info(f"Processing Excel file: {file_path}, Sheet: {sheet_name}")
            
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Excel columns found: {df.columns.tolist()}")
            
            # Clean and process each row
            for index, row in df.iterrows():
                try:
                    # Clean row data
                    data = {
                        'pump_sku': str(row['pump_sku']).strip() if pd.notna(row['pump_sku']) else None,
                        'inertia_base_part_number': str(row['inertia_base_part_number']).strip() if pd.notna(row.get('inertia_base_part_number')) else None,
                        'seismic_spring_part_number': str(row['seismic_spring_part_number']).strip() if pd.notna(row.get('seismic_spring_part_number')) else None
                    }
                    
                    if data['pump_sku']:
                        BOMDatabaseManager.insert_bom_entry(data)
                        logger.info(f"Processed row {index + 2} successfully")
                    else:
                        logger.warning(f"Skipping row {index + 2} - no pump SKU found")
                        
                except Exception as e:
                    logger.error(f"Error processing row {index + 2}: {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            raise DatabaseError(f"Failed to process Excel file: {str(e)}")

# Initialize table when module is imported
try:
    BOMDatabaseManager.create_bom_table()
except Exception as e:
    logger.error(f"Failed to initialize BOM table: {str(e)}")