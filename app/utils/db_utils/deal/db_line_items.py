from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError
from app.core.core_logging import logger # Use central app logger

class LineItemDatabaseManager:
    """Manages all line item-related database operations"""

    # The create_line_items_table() method has been removed.
    # This should be handled by a dedicated database migration script.

    @staticmethod
    def validate_line_item_data(data: Dict, is_update: bool = False) -> None:
        """Validate line item data before insertion or update."""
        required_fields = ['deal_id', 'entity_type', 'entity_id']
        if not is_update:
            for field in required_fields:
                if field not in data or data.get(field) is None:
                    raise ValueError(f"Missing required field: {field}")
        
        for field in ['amount', 'flow', 'head']:
            if field in data and data[field] is not None:
                try:
                    # This ensures the value is a valid decimal
                    Decimal(str(data[field]))
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value for numeric field: {field}")

    @staticmethod
    def insert_line_item(data: Dict) -> int:
        """Insert a new line item using a secure, parameterized query."""
        LineItemDatabaseManager.validate_line_item_data(data)
        
        try:
            # Explicitly define columns to prevent SQL injection
            query = """
                INSERT INTO line_items (
                    deal_id, entity_type, entity_id, pump_name, flow, head, 
                    description, amount
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            params = (
                data.get('deal_id'), data.get('entity_type'), data.get('entity_id'),
                data.get('pump_name'), data.get('flow'), data.get('head'),
                data.get('description'), data.get('amount')
            )
            
            inserted_id = DatabaseManager.insert_returning_id(query, params)
            logger.info(f"Successfully inserted line item with ID: {inserted_id}")
            return inserted_id

        except Exception as e:
            logger.error(f"Error inserting line item: {e}", exc_info=True)
            raise DatabaseError(f"Failed to insert line item: {e}")

    @staticmethod
    def fetch_line_items_by_deal_id(deal_id: int) -> List[Dict]:
        """Fetch all line items for a specific deal."""
        try:
            query = "SELECT * FROM line_items WHERE deal_id = %s ORDER BY created_at"
            return DatabaseManager.execute_query(query, (deal_id,))
        except Exception as e:
            logger.error(f"Error fetching line items for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch line items: {e}")

    @staticmethod
    def update_line_item(item_id: int, data: Dict) -> None:
        """Update an existing line item using a secure, parameterized query."""
        if not data:
            logger.warning("Update called with no data for line item ID {item_id}.")
            return

        LineItemDatabaseManager.validate_line_item_data(data, is_update=True)
        
        try:
            # Use a whitelist of updatable columns to prevent SQL injection
            allowed_columns = ['entity_type', 'entity_id', 'pump_name', 'flow', 'head', 'description', 'amount']
            
            set_clauses = []
            values = []
            for col in allowed_columns:
                if col in data:
                    set_clauses.append(f"{col} = %s")
                    values.append(data[col])
            
            if not set_clauses:
                raise ValueError("No valid fields provided for update.")

            # Always update the updated_at timestamp
            set_clauses.append("updated_at = %s")
            values.append(datetime.now())

            query = f"UPDATE line_items SET {', '.join(set_clauses)} WHERE id = %s"
            values.append(item_id)
            
            DatabaseManager.execute_query(query, tuple(values))
            logger.info(f"Successfully updated line item with ID: {item_id}")

        except Exception as e:
            logger.error(f"Error updating line item {item_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update line item: {e}")

    @staticmethod
    def delete_line_item(item_id: int) -> None:
        """Delete a line item."""
        try:
            query = "DELETE FROM line_items WHERE id = %s"
            DatabaseManager.execute_query(query, (item_id,))
            logger.info(f"Successfully deleted line item with ID: {item_id}")
        except Exception as e:
            logger.error(f"Error deleting line item {item_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to delete line item: {e}")

    @staticmethod
    def calculate_deal_total(deal_id: int) -> Decimal:
        """Calculate total amount for a deal based on its line items."""
        try:
            query = "SELECT COALESCE(SUM(amount), 0) as total FROM line_items WHERE deal_id = %s"
            result = DatabaseManager.execute_query(query, (deal_id,))
            return Decimal(str(result[0]['total']))
        except Exception as e:
            logger.error(f"Error calculating deal total for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to calculate deal total: {e}")

    # The bulk_insert method has been removed. A proper implementation would require
    # using advanced features of the underlying database driver (e.g., psycopg2.extras.execute_values)
    # which is beyond the scope of the current DatabaseManager abstraction.
    # A simple loop of `insert_line_item` is safer than an insecure bulk method.