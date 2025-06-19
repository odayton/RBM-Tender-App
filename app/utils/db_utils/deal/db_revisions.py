# app/utils/db_utils/db_revisions.py

from typing import Dict, List, Optional
import logging
from datetime import datetime
from app.core.core_database import DatabaseManager, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RevisionDatabaseManager:
    """Manages all revision-related database operations"""

    @staticmethod
    def create_revisions_table() -> None:
        """Creates revisions table with PostgreSQL optimizations"""
        try:
            query = """
                CREATE TABLE IF NOT EXISTS revisions (
                    id SERIAL PRIMARY KEY,
                    deal_id INTEGER NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
                    version TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(deal_id, version)
                );

                CREATE INDEX IF NOT EXISTS idx_revisions_deal ON revisions(deal_id);
                CREATE INDEX IF NOT EXISTS idx_revisions_version ON revisions(version);
            """

            DatabaseManager.execute_query(query)
            logger.info("Revisions table created successfully")
        except Exception as e:
            logger.error(f"Error creating revisions table: {str(e)}")
            raise DatabaseError(f"Failed to create revisions table: {str(e)}")

    @staticmethod
    def validate_revision_data(data: Dict) -> None:
        """Validate revision data before insertion/update"""
        required_fields = ['deal_id', 'version']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Missing required field: {field}")

        # Validate version format (e.g., "1.0", "2.1")
        version = str(data['version'])
        if not version.replace('.', '').isdigit():
            raise ValueError("Invalid version format. Expected format: X.Y")

    @staticmethod
    def insert_revision(data: Dict) -> int:
        """Insert a new revision"""
        try:
            # Validate data
            RevisionDatabaseManager.validate_revision_data(data)

            # Add timestamps
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
                INSERT INTO revisions ({fields})
                VALUES ({placeholders})
                RETURNING id
            """
            
            return DatabaseManager.insert_returning_id(query, tuple(data.values()))

        except Exception as e:
            logger.error(f"Error inserting revision: {str(e)}")
            raise DatabaseError(f"Failed to insert revision: {str(e)}")

    @staticmethod
    def fetch_revisions_by_deal_id(deal_id: int) -> List[Dict]:
        """Fetch all revisions for a specific deal"""
        try:
            query = """
                SELECT *
                FROM revisions
                WHERE deal_id = %s
                ORDER BY 
                    CAST(SPLIT_PART(version, '.', 1) AS INTEGER),
                    CAST(SPLIT_PART(version, '.', 2) AS INTEGER)
            """
            return DatabaseManager.execute_query(query, (deal_id,))

        except Exception as e:
            logger.error(f"Error fetching revisions: {str(e)}")
            raise DatabaseError(f"Failed to fetch revisions: {str(e)}")

    @staticmethod
    def get_latest_revision(deal_id: int) -> Optional[Dict]:
        """Get the latest revision for a deal"""
        try:
            query = """
                SELECT *
                FROM revisions
                WHERE deal_id = %s
                ORDER BY 
                    CAST(SPLIT_PART(version, '.', 1) AS INTEGER) DESC,
                    CAST(SPLIT_PART(version, '.', 2) AS INTEGER) DESC
                LIMIT 1
            """
            results = DatabaseManager.execute_query(query, (deal_id,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching latest revision: {str(e)}")
            raise DatabaseError(f"Failed to fetch latest revision: {str(e)}")

    @staticmethod
    def generate_next_version(deal_id: int) -> str:
        """Generate the next version number for a deal"""
        try:
            latest_revision = RevisionDatabaseManager.get_latest_revision(deal_id)
            
            if not latest_revision:
                return "1.0"
                
            current_version = latest_revision['version']
            major, minor = map(int, current_version.split('.'))
            
            return f"{major}.{minor + 1}"

        except Exception as e:
            logger.error(f"Error generating next version: {str(e)}")
            raise DatabaseError(f"Failed to generate next version: {str(e)}")

    @staticmethod
    def update_revision(revision_id: int, data: Dict) -> None:
        """Update an existing revision"""
        try:
            # Add updated timestamp
            data['updated_at'] = datetime.now()

            fields = [f"{k} = %s" for k in data.keys()]
            query = f"""
                UPDATE revisions 
                SET {', '.join(fields)}
                WHERE id = %s
            """
            values = list(data.values()) + [revision_id]
            DatabaseManager.execute_query(query, tuple(values))

        except Exception as e:
            logger.error(f"Error updating revision: {str(e)}")
            raise DatabaseError(f"Failed to update revision: {str(e)}")

    @staticmethod
    def fetch_revision_by_id(revision_id: int) -> Optional[Dict]:
        """Fetch a specific revision by ID"""
        try:
            query = """
                SELECT * 
                FROM revisions 
                WHERE id = %s
            """
            results = DatabaseManager.execute_query(query, (revision_id,))
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error fetching revision: {str(e)}")
            raise DatabaseError(f"Failed to fetch revision: {str(e)}")

# Initialize table when module is imported
try:
    RevisionDatabaseManager.create_revisions_table()
except Exception as e:
    logger.error(f"Failed to initialize revisions table: {str(e)}")