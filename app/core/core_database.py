from typing import Optional, Any, Dict, List
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from app.extensions import db # Import the central db instance
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger

class DatabaseManager:
    """
    A collection of static helper methods for executing raw SQL queries
    using the application's primary SQLAlchemy session.
    """

    # The init_app method is no longer needed, as this class no longer manages a separate engine.
    # The Flask-SQLAlchemy `db` object is initialized in the app factory.

    @staticmethod
    @contextmanager
    def session_scope():
        """
        Provide a transactional scope around a series of operations.
        This is a wrapper around the standard db.session.
        """
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Session transaction failed. Rolling back. Error: {e}", exc_info=True)
            raise DatabaseError(f"Database transaction failed: {e}")

    @staticmethod
    def execute_query(query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Executes a raw SQL query and returns a list of dictionaries.

        Args:
            query (str): The SQL query to execute.
            params (Dict, optional): Parameters to bind to the query.

        Returns:
            A list of rows, where each row is a dictionary.
        """
        try:
            result_proxy = db.session.execute(text(query), params or {})
            
            # For statements like INSERT/UPDATE/DELETE, there are no rows to fetch.
            if result_proxy.returns_rows:
                # .mappings() provides an iterator of dictionary-like row objects.
                return [dict(row) for row in result_proxy.mappings()]
            else:
                db.session.commit() # Commit changes for non-returning statements
                return []
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Query execution failed: {e}", exc_info=True)
            raise DatabaseError(f"Query execution failed: {e}")

    @staticmethod
    def insert_returning_id(query: str, params: Optional[Dict] = None) -> Optional[int]:
        """
        Executes an INSERT statement and returns the new primary key.
        NOTE: This is typically for PostgreSQL. For other DBs, behavior may vary.
        """
        try:
            result = db.session.execute(text(query), params or {}).scalar_one_or_none()
            db.session.commit()
            return result
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Insert returning ID failed: {e}", exc_info=True)
            raise DatabaseError(f"Insert returning ID failed: {e}")

    @staticmethod
    def bulk_insert(table_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Securely bulk inserts data into a specified table using the ORM's bulk insert mapping.
        """
        if not data:
            return
        
        # This approach is safe from SQL injection as SQLAlchemy handles the mapping.
        try:
            # Get the table object from SQLAlchemy's metadata
            table = db.metadata.tables.get(table_name)
            if table is None:
                raise DatabaseError(f"Table '{table_name}' not found in SQLAlchemy metadata.")
            
            # Use the core session to execute the bulk insert
            db.session.bulk_insert_mappings(table, data)
            db.session.commit()
            logger.info(f"Successfully bulk inserted {len(data)} records into '{table_name}'.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Bulk insert into '{table_name}' failed: {e}", exc_info=True)
            raise DatabaseError(f"Bulk insert failed: {e}")