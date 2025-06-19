# app/core/core_database.py

from typing import Optional, Any, Dict, List, Union
from contextlib import contextmanager
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from app.app_logging import app_logger
from app.app_constants import (
    DB_CONNECTION_TIMEOUT,
    MAX_POOL_SIZE,
    DEFAULT_PAGE_SIZE,
    DB_POOL_RECYCLE
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Centralized database management system providing consistent database operations,
    connection pooling, session management, and error handling.
    """
    
    def __init__(self, app=None):
        self.app = app
        self._engine = None
        self._session_factory = None
        self.Session = None
        self.metadata = MetaData()
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Initialize database with application"""
        self.app = app
        self._setup_engine()
        self._setup_session()
        self._register_events()
        
        logger.info("Database manager initialized successfully")

    def _setup_engine(self) -> None:
        """Configure database engine with connection pooling"""
        try:
            self._engine = create_engine(
                self.app.config['SQLALCHEMY_DATABASE_URI'],
                poolclass=QueuePool,
                pool_size=MAX_POOL_SIZE,
                max_overflow=5,
                pool_timeout=DB_CONNECTION_TIMEOUT,
                pool_pre_ping=True,
                pool_recycle=DB_POOL_RECYCLE,
                echo=self.app.debug
            )
            logger.info("Database engine created successfully")
        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise

    def _setup_session(self) -> None:
        """Configure session factory and scoped session"""
        try:
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )
            self.Session = scoped_session(self._session_factory)
            logger.info("Database session configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure database session: {str(e)}")
            raise

    def _register_events(self) -> None:
        """Register database event listeners"""
        
        @self._engine.event.listens_for(self._engine, 'connect')
        def on_connect(dbapi_connection, connection_record):
            """Handle new connections"""
            logger.debug("New database connection established")
            
            # Set pragmas for SQLite
            if self.app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        @self._engine.event.listens_for(self._engine, 'checkout')
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Verify connection on checkout"""
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SELECT 1")
            except Exception:
                logger.error("Connection verification failed")
                raise
            finally:
                cursor.close()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session operation failed: {str(e)}")
            raise
        finally:
            session.close()

    def execute_query(
        self, 
        query: str, 
        params: Optional[Union[Dict, tuple]] = None,
        fetch: bool = True
    ) -> Optional[List[Dict]]:
        """Execute a raw SQL query with comprehensive error handling"""
        with self.session_scope() as session:
            try:
                start_time = datetime.now()
                
                if isinstance(params, dict):
                    result = session.execute(text(query), params)
                else:
                    result = session.execute(text(query), params or ())
                
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log query execution
                app_logger.log_db_query(query, duration)
                
                return [dict(row) for row in result] if fetch else None

            except SQLAlchemyError as e:
                logger.error(f"Query execution failed: {str(e)}")
                raise

    def bulk_insert(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """Bulk insert data into specified table"""
        if not data:
            return
            
        columns = data[0].keys()
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join([':' + col for col in columns])})
        """
        
        with self.session_scope() as session:
            try:
                session.execute(text(query), data)
            except SQLAlchemyError as e:
                logger.error(f"Bulk insert failed: {str(e)}")
                raise

    def paginate_query(
        self,
        query: Any,
        page: int = 1,
        per_page: int = DEFAULT_PAGE_SIZE
    ) -> Dict[str, Any]:
        """Paginate a SQLAlchemy query"""
        try:
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        except SQLAlchemyError as e:
            logger.error(f"Pagination failed: {str(e)}")
            raise

    def get_table_stats(self) -> Dict[str, Any]:
        """Get database table statistics"""
        stats = {}
        with self.session_scope() as session:
            try:
                # Get table names
                if self.app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
                    tables = session.execute(text("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """))
                else:  # SQLite
                    tables = session.execute(text("""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table'
                    """))

                # Get stats for each table
                for table in tables:
                    table_name = table[0]
                    row_count = session.execute(
                        text(f"SELECT COUNT(*) FROM {table_name}")
                    ).scalar()
                    stats[table_name] = {
                        'row_count': row_count
                    }

                return stats
            except SQLAlchemyError as e:
                logger.error(f"Failed to get table stats: {str(e)}")
                raise

    def verify_connection(self) -> bool:
        """Verify database connection is working"""
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection verification failed: {str(e)}")
            return False

    def get_connection_pool_status(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        return {
            'pool_size': self._engine.pool.size(),
            'checkedin': self._engine.pool.checkedin(),
            'checkedout': self._engine.pool.checkedout(),
            'overflow': self._engine.pool.overflow()
        }

# Create database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db_session():
    """Get a database session"""
    return db_manager.Session()

@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    with db_manager.session_scope() as session:
        yield session