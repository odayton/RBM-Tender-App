from typing import Dict, List, Optional
from datetime import datetime
from app.core.core_database import DatabaseManager, DatabaseError
from app.core.core_logging import logger # Use central app logger

class RevisionDatabaseManager:
    """Manages all revision-related database operations"""

    # The create_revisions_table() method has been removed.
    # This should be handled by a dedicated database migration script.

    @staticmethod
    def validate_revision_data(data: Dict) -> None:
        """Validate revision data before insertion/update"""
        required_fields = ['deal_id', 'version']
        for field in required_fields:
            if field not in data or data.get(field) is None:
                raise ValueError(f"Missing required field: {field}")

        version = str(data['version'])
        parts = version.split('.')
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise ValueError("Invalid version format. Expected format: X.Y (e.g., '1.0')")

    @staticmethod
    def insert_revision(data: Dict) -> int:
        """Insert a new revision using a secure, parameterized query."""
        RevisionDatabaseManager.validate_revision_data(data)
        
        try:
            query = """
                INSERT INTO revisions (deal_id, version, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            now = datetime.now()
            params = (
                data.get('deal_id'),
                data.get('version'),
                data.get('description'),
                now,
                now
            )
            
            inserted_id = DatabaseManager.insert_returning_id(query, params)
            logger.info(f"Successfully inserted revision {data.get('version')} for deal ID {data.get('deal_id')}. New revision ID: {inserted_id}")
            return inserted_id

        except Exception as e:
            logger.error(f"Error inserting revision: {e}", exc_info=True)
            # Check for unique constraint violation
            if 'unique constraint' in str(e).lower():
                raise DatabaseError(f"Version '{data.get('version')}' already exists for this deal.")
            raise DatabaseError(f"Failed to insert revision: {e}")

    @staticmethod
    def fetch_revisions_by_deal_id(deal_id: int) -> List[Dict]:
        """Fetch all revisions for a specific deal, sorted naturally by version number."""
        try:
            # Casting version parts to integer ensures correct sorting (e.g., 1.10 after 1.9)
            query = """
                SELECT * FROM revisions
                WHERE deal_id = %s
                ORDER BY 
                    CAST(SPLIT_PART(version, '.', 1) AS INTEGER) DESC,
                    CAST(SPLIT_PART(version, '.', 2) AS INTEGER) DESC
            """
            return DatabaseManager.execute_query(query, (deal_id,))
        except Exception as e:
            logger.error(f"Error fetching revisions for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch revisions: {e}")

    @staticmethod
    def get_latest_revision(deal_id: int) -> Optional[Dict]:
        """Get the latest revision for a deal using natural version sorting."""
        try:
            revisions = RevisionDatabaseManager.fetch_revisions_by_deal_id(deal_id)
            return revisions[0] if revisions else None
        except Exception as e:
            logger.error(f"Error fetching latest revision for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch latest revision: {e}")

    @staticmethod
    def generate_next_version(deal_id: int) -> str:
        """Generate the next minor version number for a deal (e.g., 1.0 -> 1.1)."""
        try:
            latest_revision = RevisionDatabaseManager.get_latest_revision(deal_id)
            if not latest_revision:
                return "1.0"
            
            current_version = latest_revision['version']
            major, minor = map(int, current_version.split('.'))
            return f"{major}.{minor + 1}"
        except Exception as e:
            logger.error(f"Error generating next version for deal ID {deal_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to generate next version: {e}")

    @staticmethod
    def update_revision(revision_id: int, data: Dict) -> None:
        """Update an existing revision using a secure, parameterized query."""
        if not data:
            logger.warning(f"Update called with no data for revision ID {revision_id}.")
            return

        try:
            # Use a whitelist of updatable columns to prevent SQL injection
            allowed_columns = ['version', 'description']
            
            set_clauses = []
            values = []
            for col in allowed_columns:
                if col in data:
                    set_clauses.append(f"{col} = %s")
                    values.append(data[col])
            
            if not set_clauses:
                raise ValueError("No valid fields provided for update.")

            set_clauses.append("updated_at = %s")
            values.append(datetime.now())

            query = f"UPDATE revisions SET {', '.join(set_clauses)} WHERE id = %s"
            values.append(revision_id)
            
            DatabaseManager.execute_query(query, tuple(values))
            logger.info(f"Successfully updated revision with ID: {revision_id}")

        except Exception as e:
            logger.error(f"Error updating revision {revision_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update revision: {e}")

    @staticmethod
    def fetch_revision_by_id(revision_id: int) -> Optional[Dict]:
        """Fetch a specific revision by ID."""
        try:
            query = "SELECT * FROM revisions WHERE id = %s"
            results = DatabaseManager.execute_query(query, (revision_id,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching revision ID {revision_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to fetch revision: {e}")