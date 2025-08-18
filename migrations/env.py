import logging
import os
import sys
import traceback
from logging.config import fileConfig
from pathlib import Path

from flask import current_app
from alembic import context
from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the Python path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger('alembic.env')

def get_engine():
    """Get the database engine with comprehensive error handling."""
    try:
        # Try Flask-SQLAlchemy v3+ approach first
        if hasattr(current_app.extensions['migrate'].db, 'engine'):
            return current_app.extensions['migrate'].db.engine
        
        # Fallback to older Flask-SQLAlchemy approach
        if hasattr(current_app.extensions['migrate'].db, 'get_engine'):
            return current_app.extensions['migrate'].db.get_engine()
        
        # Direct engine access
        return current_app.extensions['migrate'].db.engine
        
    except (TypeError, AttributeError, KeyError) as e:
        logger.error(f"Failed to get engine from Flask app: {e}")
        logger.error("Available extensions: %s", list(current_app.extensions.keys()))
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting engine: {e}")
        logger.error(traceback.format_exc())
        raise

def get_engine_url():
    """Get the database URL with proper error handling and validation."""
    try:
        engine = get_engine()
        
        # Handle different URL rendering methods
        if hasattr(engine.url, 'render_as_string'):
            url = engine.url.render_as_string(hide_password=False)
        else:
            url = str(engine.url)
        
        # Escape % characters for Alembic
        url = url.replace('%', '%%')
        
        logger.info(f"Database URL configured: {url.split('@')[-1] if '@' in url else url}")
        return url
        
    except Exception as e:
        logger.error(f"Failed to get engine URL: {e}")
        logger.error(traceback.format_exc())
        raise

def get_metadata():
    """Get the database metadata with comprehensive error handling."""
    try:
        target_db = current_app.extensions['migrate'].db
        
        # Handle Flask-SQLAlchemy v3+ metadata structure
        if hasattr(target_db, 'metadatas'):
            metadata = target_db.metadatas[None]
        else:
            metadata = target_db.metadata
            
        if metadata is None:
            raise ValueError("Database metadata is None")
            
        logger.info(f"Retrieved metadata with {len(metadata.tables)} tables")
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to get metadata: {e}")
        logger.error(traceback.format_exc())
        raise

def import_models():
    """Import all models to ensure they are registered with SQLAlchemy."""
    try:
        # Import base models first
        from app.models import base_model
        
        # Import all model modules to ensure they are registered
        from app.models import (
            user_model,
            customers,
            deals,
            crm,
            products,
            pumps
        )
        
        # Import specific models to ensure they're loaded
        from app.models.customers.company_model import Company
        from app.models.customers.customer_model import Contact
        from app.models.deals.deal_models import Deal
        from app.models.crm.activity_models import Activity
        from app.models.crm.task_models import Task
        from app.models.user_model import User
        from app.models.pumps.pump_model import Pump
        from app.models.products.product_model import Product
        
        logger.info("✅ All models imported successfully")
        
        # Log table count for verification
        metadata = get_metadata()
        table_names = list(metadata.tables.keys())
        logger.info(f"📋 Registered tables: {', '.join(sorted(table_names))}")
        
    except ImportError as e:
        logger.warning(f"⚠️  Some models could not be imported: {e}")
        logger.warning("This may be normal if some models are optional")
    except Exception as e:
        logger.error(f"❌ Error importing models: {e}")
        logger.error(traceback.format_exc())
        raise

def validate_database_connection():
    """Validate that we can connect to the database."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Test a simple query
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection validated successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection validation failed: {e}")
        return False

def check_migration_table():
    """Check if the alembic_version table exists and is accessible."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='alembic_version'
            """))
            exists = result.fetchone() is not None
            
            if exists:
                # Get current version
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                current_version = result.fetchone()
                logger.info(f"Alembic version table found. Current version: {current_version[0] if current_version else 'None'}")
            else:
                logger.info("Alembic version table not found (this is normal for new databases)")
                
        return True
    except Exception as e:
        logger.error(f"Failed to check migration table: {e}")
        return False

def create_backup_before_migration():
    """Create a backup of the database before running migrations."""
    try:
        from datetime import datetime
        import shutil
        
        # Get database file path
        engine = get_engine()
        db_url = str(engine.url)
        
        if 'sqlite' in db_url:
            # Extract file path from SQLite URL
            db_path = db_url.replace('sqlite:///', '').replace('sqlite://', '')
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.getcwd(), db_path)
            
            if os.path.exists(db_path):
                # Create backup directory
                backup_dir = Path("migrations/backups")
                backup_dir.mkdir(exist_ok=True)
                
                # Create backup filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}_{os.path.basename(db_path)}"
                backup_path = backup_dir / backup_name
                
                # Copy database file
                shutil.copy2(db_path, backup_path)
                logger.info(f"Database backup created: {backup_path}")
                return str(backup_path)
        
        logger.info("Database backup skipped (not SQLite or file not found)")
        return None
        
    except Exception as e:
        logger.warning(f"Failed to create database backup: {e}")
        return None

# Initialize database connection and validation
try:
    # Set up the database URL
    config.set_main_option('sqlalchemy.url', get_engine_url())
    logger.info("Database URL configured successfully")
    
    # Validate database connection
    if not validate_database_connection():
        raise RuntimeError("Database connection validation failed")
    
    # Check migration table
    check_migration_table()
    
    # Import models before setting up metadata
    import_models()
    
    # Set up target metadata
    target_metadata = get_metadata()
    logger.info("Target metadata configured successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize migration environment: {e}")
    logger.error(traceback.format_exc())
    raise

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the
    Engine creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    try:
        logger.info("Running migrations in offline mode")
        
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()
        logger.info("Offline migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Offline migration failed: {e}")
        logger.error(traceback.format_exc())
        raise

def run_migrations_online():
    """Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate
    a connection with the context.
    """
    try:
        logger.info("Running migrations in online mode")
        
        # Create backup before migration
        backup_path = create_backup_before_migration()
        
        # this callback is used to prevent an auto-migration from being generated
        # when there are no changes to the schema
        # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
        def process_revision_directives(context, revision, directives):
            if getattr(config.cmd_opts, 'autogenerate', False):
                script = directives[0]
                if script.upgrade_ops.is_empty():
                    directives[:] = []
                    logger.info('No changes in schema detected.')

        # Get configuration arguments
        conf_args = current_app.extensions['migrate'].configure_args
        if conf_args.get("process_revision_directives") is None:
            conf_args["process_revision_directives"] = process_revision_directives

        # Get the engine
        connectable = get_engine()

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                **conf_args
            )

            with context.begin_transaction():
                context.run_migrations()
                
        logger.info("Online migrations completed successfully")
        if backup_path:
            logger.info(f"Backup available at: {backup_path}")
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}")
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"Online migration failed: {e}")
        logger.error(traceback.format_exc())
        raise

def main():
    """Main migration function with comprehensive error handling."""
    try:
        logger.info("Starting migration process...")
        
        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
            
        logger.info("Migration process completed successfully")
        
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == '__main__':
    main()
else:
    main()
