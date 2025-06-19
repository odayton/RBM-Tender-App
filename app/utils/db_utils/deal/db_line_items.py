# app/utils/db_utils/db_line_items.py

from typing import Dict, List, Optional
import logging
from datetime import datetime
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LineItemDatabaseManager:
    """Manages all line item-related database operations"""

    @staticmethod
    def create_line_items_table() -> None:
        """Creates line items table with PostgreSQL optimizations"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS line_items (
                    id SERIAL PRIMARY KEY,
                    deal_id INTEGER REFERENCES deals(id) ON DELETE CASCADE,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    pump_name TEXT,
                    flow DECIMAL(10, 2),
                    head DECIMAL(10, 2),
                    description TEXT,
                    amount DECIMAL(15, 2),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_line_items_deal ON line_items(deal_id);
                CREATE INDEX IF NOT EXISTS idx_line_items_entity ON line_items(entity_type, entity_id);
            """

            DatabaseManager.execute_query(query)
            logger.info("Line items table created successfully")
        except Exception as e:
            logger.error(f"Error creating line items table: {str(e)}")
            raise DatabaseError(f"Failed to create line items table: {str(e)}")

    @staticmethod
    def validate_line_item_data(data: Dict) -> None:
        """Validate line item data before insertion/update"""
        required_fields = ['deal_id', 'entity_type', 'entity_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric values
        if 'amount' in data and data['amount'] is not None:
            try:
                data['amount'] = Decimal(str(data['amount']))
            except (ValueError, TypeError):
                raise ValueError("Invalid amount value")

        if 'flow' in data and data['flow'] is not None:
            try:
                data['flow'] = Decimal(str(data['flow']))
            except (ValueError, TypeError):
                raise ValueError("Invalid flow value")

        if 'head' in data and data['head'] is not None:
            try:
                data['head'] = Decimal(str(data['head']))
            except (ValueError, TypeError):
                raise ValueError("Invalid head value")

    @staticmethod
    def insert_line_item(data: Dict) -> int:
        """Insert a new line item"""
        try:
            # Validate data
            LineItemDatabaseManager.validate_line_item_data(data)

            # Add timestamps
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO line_items ({fields})
                VALUES ({placeholders})
                RETURNING id
            """
            
            return DatabaseManager.insert_returning_id(query, tuple(data.values()))

        except Exception as e:
            logger.error(f"Error inserting line item: {str(e)}")
            raise DatabaseError(f"Failed to insert line item: {str(e)}")

    @staticmethod
    def fetch_line_items_by_deal_id(deal_id: int) -> List[Dict]:
        """Fetch all line items for a specific deal"""
        try:
            query = """
                SELECT *
                FROM line_items
                WHERE deal_id = %s
                ORDER BY created_at
            """
            return DatabaseManager.execute_query(query, (deal_id,))

        except Exception as e:
            logger.error(f"Error fetching line items: {str(e)}")
            raise DatabaseError(f"Failed to fetch line items: {str(e)}")

    @staticmethod
    def update_line_item(item_id: int, data: Dict) -> None:
        """Update an existing line item"""
        try:
            # Add updated timestamp
            data['updated_at'] = datetime.now()

            fields = [f"{k} = %s" for k in data.keys()]
            query = f"""
                UPDATE line_items 
                SET {', '.join(fields)}
                WHERE id = %s
            """
            values = list(data.values()) + [item_id]
            DatabaseManager.execute_query(query, tuple(values))

        except Exception as e:
            logger.error(f"Error updating line item: {str(e)}")
            raise DatabaseError(f"Failed to update line item: {str(e)}")

    @staticmethod
    def delete_line_item(item_id: int) -> None:
        """Delete a line item"""
        try:
            query = "DELETE FROM line_items WHERE id = %s"
            DatabaseManager.execute_query(query, (item_id,))

        except Exception as e:
            logger.error(f"Error deleting line item: {str(e)}")
            raise DatabaseError(f"Failed to delete line item: {str(e)}")

    @staticmethod
    def calculate_deal_total(deal_id: int) -> Decimal:
        """Calculate total amount for a deal based on its line items"""
        try:
            query = """
                SELECT COALESCE(SUM(amount), 0) as total
                FROM line_items
                WHERE deal_id = %s
            """
            result = DatabaseManager.execute_query(query, (deal_id,))
            return Decimal(str(result[0]['total']))

        except Exception as e:
            logger.error(f"Error calculating deal total: {str(e)}")
            raise DatabaseError(f"Failed to calculate deal total: {str(e)}")

    @staticmethod
    def bulk_insert_line_items(items: List[Dict]) -> None:
        """Bulk insert multiple line items"""
        try:
            if not items:
                return

            # Validate all items first
            for item in items:
                LineItemDatabaseManager.validate_line_item_data(item)
                item['created_at'] = datetime.now()
                item['updated_at'] = datetime.now()

            fields = items[0].keys()
            placeholders = ', '.join(['%s'] * len(fields))
            
            query = f"""
                INSERT INTO line_items ({', '.join(fields)})
                VALUES ({placeholders})
            """

            values = [tuple(item.values()) for item in items]
            DatabaseManager.execute_many(query, values)

        except Exception as e:
            logger.error(f"Error bulk inserting line items: {str(e)}")
            raise DatabaseError(f"Failed to bulk insert line items: {str(e)}")

# Initialize table when module is imported
try:
    LineItemDatabaseManager.create_line_items_table()
except Exception as e:
    logger.error(f"Failed to initialize line items table: {str(e)}")