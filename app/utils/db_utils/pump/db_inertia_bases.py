from typing import Dict, Any, List, Optional
from app.core.core_database import DatabaseManager, session_scope
# Removed the non-existent 'InertiaBaseUsage' model
from app.models import InertiaBase

class InertiaBaseManager:
    """
    Manages database operations for inertia bases.
    """

    @staticmethod
    def create_inertia_bases_table():
        """
        Creates the inertia_bases table in the database.
        This is a legacy method and will be replaced by Flask-Migrate.
        """
        query = """
        CREATE TABLE IF NOT EXISTS inertia_bases (
            id SERIAL PRIMARY KEY,
            part_number VARCHAR(255) UNIQUE NOT NULL,
            dimensions VARCHAR(255),
            weight_kg NUMERIC(10, 2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        with session_scope() as session:
            session.execute(query)

    @staticmethod
    def get_by_part_number(part_number: str) -> Optional[Dict[str, Any]]:
        """Retrieves an inertia base by its part number."""
        query = "SELECT * FROM inertia_bases WHERE part_number = %(part_number)s"
        params = {'part_number': part_number}
        with session_scope() as session:
            result = session.execute(query, params).fetchone()
            return dict(result) if result else None

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves all inertia bases with pagination."""
        query = "SELECT * FROM inertia_bases ORDER BY part_number LIMIT %(limit)s OFFSET %(offset)s"
        params = {'limit': limit, 'offset': offset}
        with session_scope() as session:
            results = session.execute(query, params).fetchall()
            return [dict(row) for row in results]