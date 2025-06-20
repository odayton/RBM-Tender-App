from typing import Dict, Any, List, Optional
from app.core.core_database import DatabaseManager, session_scope
from app.models import Pump  # Removed HistoricPumpData as it no longer exists

class PumpDatabaseManager:
    """
    Manages database operations for pump data.
    """

    @staticmethod
    def get_pump_by_sku(sku: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single pump's details from the database by its SKU.
        
        Args:
            sku (str): The SKU of the pump to retrieve.
            
        Returns:
            Optional[Dict[str, Any]]: A dictionary of the pump's data or None if not found.
        """
        query = "SELECT * FROM general_pump_details WHERE sku = %(sku)s"
        params = {'sku': sku}
        
        with session_scope() as session:
            result = session.execute(query, params).fetchone()
            return dict(result) if result else None

    @staticmethod
    def get_all_pumps(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all pumps with pagination.
        
        Args:
            limit (int): The number of records to return.
            offset (int): The starting point for the records.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a pump.
        """
        query = "SELECT * FROM general_pump_details ORDER BY name LIMIT %(limit)s OFFSET %(offset)s"
        params = {'limit': limit, 'offset': offset}
        
        with session_scope() as session:
            results = session.execute(query, params).fetchall()
            return [dict(row) for row in results]

    @staticmethod
    def search_pumps(search_term: str) -> List[Dict[str, Any]]:
        """
        Searches for pumps by name or SKU.
        
        Args:
            search_term (str): The term to search for.
            
        Returns:
            List[Dict[str, Any]]: A list of matching pumps.
        """
        query = """
            SELECT * FROM general_pump_details 
            WHERE name ILIKE %(term)s OR sku ILIKE %(term)s
        """
        params = {'term': f'%{search_term}%'}
        
        with session_scope() as session:
            results = session.execute(query, params).fetchall()
            return [dict(row) for row in results]