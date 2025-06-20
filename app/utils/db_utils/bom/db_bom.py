from typing import Dict, List, Optional
import pandas as pd
from app.core.core_database import DatabaseManager, DatabaseError
from app.core.core_logging import logger # Use central app logger

class BOMDatabaseManager:
    """Manages all BOM-related database operations"""

    # The create_bom_table() method has been removed.
    # This should be handled by a dedicated database migration script.

    @staticmethod
    def validate_bom_data(data: Dict) -> None:
        """Validate BOM data before insertion/update"""
        if not data.get('pump_sku'):
            raise ValueError("Pump SKU is required for a BOM entry.")

    @staticmethod
    def upsert_bom_entry(data: Dict) -> None:
        """
        Insert a new BOM entry or update it if it already exists.
        This operation is now 'upsert' (update or insert).
        """
        try:
            logger.info(f"Attempting to upsert BOM entry for pump SKU: {data.get('pump_sku')}")
            
            # Validate data before proceeding
            BOMDatabaseManager.validate_bom_data(data)
            pump_sku = data['pump_sku']

            # This single query will UPDATE if the pump_sku exists, or INSERT if it does not.
            # This is more efficient and safer than performing a SELECT then an INSERT/UPDATE.
            # This syntax is specific to PostgreSQL.
            query = """
                INSERT INTO bom (pump_sku, inertia_base_part_number, seismic_spring_part_number)
                VALUES (%s, %s, %s)
                ON CONFLICT (pump_sku) DO UPDATE SET
                    inertia_base_part_number = EXCLUDED.inertia_base_part_number,
                    seismic_spring_part_number = EXCLUDED.seismic_spring_part_number;
            """
            params = (
                pump_sku,
                data.get('inertia_base_part_number'),
                data.get('seismic_spring_part_number'),
            )
            
            DatabaseManager.execute_query(query, params)
            logger.info(f"Successfully upserted BOM entry for pump SKU: {pump_sku}")

        except Exception as e:
            logger.error(f"Error upserting BOM entry: {e}", exc_info=True)
            raise DatabaseError(f"Failed to upsert BOM entry: {e}")

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
            logger.error(f"Error fetching BOM entries: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch BOM entries: {e}")

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
            logger.error(f"Error fetching BOM for pump '{pump_sku}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch BOM for pump '{pump_sku}': {e}")

    @staticmethod
    def process_bom_excel(file_path: str, sheet_name: Optional[str] = None) -> None:
        """Process BOM data from an Excel file"""
        try:
            logger.info(f"Processing Excel file: {file_path}, Sheet: {sheet_name or 'default'}")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Excel columns found: {df.columns.tolist()}")
            
            processed_count = 0
            for index, row in df.iterrows():
                try:
                    data = {
                        'pump_sku': str(row['pump_sku']).strip() if pd.notna(row.get('pump_sku')) else None,
                        'inertia_base_part_number': str(row['inertia_base_part_number']).strip() if pd.notna(row.get('inertia_base_part_number')) else None,
                        'seismic_spring_part_number': str(row['seismic_spring_part_number']).strip() if pd.notna(row.get('seismic_spring_part_number')) else None
                    }
                    
                    if data['pump_sku']:
                        BOMDatabaseManager.upsert_bom_entry(data)
                        processed_count += 1
                    else:
                        logger.warning(f"Skipping row {index + 2} - no pump SKU found.")
                        
                except Exception as e:
                    logger.error(f"Error processing row {index + 2}: {e}", exc_info=True)
                    # Continue to next row instead of failing the whole import
            
            logger.info(f"Successfully processed {processed_count} rows from Excel file.")

        except Exception as e:
            logger.error(f"Error processing Excel file '{file_path}': {e}", exc_info=True)
            raise DatabaseError(f"Failed to process Excel file: {e}")