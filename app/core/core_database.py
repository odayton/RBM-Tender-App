from contextlib import contextmanager
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from app.core.core_logging import logger

# This context manager provides a standardized way to handle session commits,
# rollbacks, and closing, which is useful for the legacy db_utils.
@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = db.session
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        # The session is managed by Flask-SQLAlchemy's scoped_session,
        # so db.session.remove() is typically called at the end of a request,
        # not here. Leaving the 'finally' block empty is standard practice.
        pass

class DatabaseManager:
    """
    This class contains legacy raw SQL execution methods.
    The goal is to phase this out in favor of the ORM.
    """
    @staticmethod
    def execute_query(query: str, params: dict = None, fetch: str = None):
        try:
            with session_scope() as session:
                result = session.execute(db.text(query), params)
                if fetch == 'one':
                    return result.fetchone()
                elif fetch == 'all':
                    return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"Failed to execute query: {e}")
            # Re-raise as a more generic exception or handle as needed
            raise