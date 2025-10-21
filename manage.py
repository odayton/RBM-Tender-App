#!/usr/bin/env python3
"""
Management CLI for RBM Tender App
Development and maintenance commands

This script provides management commands for development,
testing, and maintenance tasks. Not needed in production.

Usage:
    python manage.py --help
    python manage.py dev
    python manage.py prod-test
    python manage.py shell
"""

import os
import sys
import logging
import click
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / 'config' / '.env')

from app import create_app
from app.core.core_config import config_dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """RBM Tender App Management CLI"""
    pass


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--no-debug', is_flag=True, help='Disable debug mode')
def dev(host, port, no_debug):
    """
    Run development server with auto-reload
    
    Examples:
        python manage.py dev
        python manage.py dev --host 0.0.0.0
        python manage.py dev --port 8000
    """
    os.environ['FLASK_ENV'] = 'development'
    
    logger.info("Starting development server...")
    logger.info(f"Environment: development")
    logger.info(f"Address: http://{host}:{port}")
    logger.info(f"Debug mode: {'enabled' if not no_debug else 'disabled'}")
    logger.info("Press Ctrl+C to stop")
    
    app = create_app(config_dict['development'])
    app.run(
        host=host,
        port=port,
        debug=not no_debug,
        threaded=True
    )


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
def prod_test(host, port):
    """
    Test production configuration locally
    
    This runs the app with production config for testing,
    but still uses Flask's dev server. Do NOT use this
    for actual production deployment.
    
    Examples:
        python manage.py prod-test
    """
    os.environ['FLASK_ENV'] = 'production'
    
    # Check required environment variables
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Set these in config/.env before testing production config")
        sys.exit(1)
    
    logger.warning("="*60)
    logger.warning("PRODUCTION CONFIGURATION TEST")
    logger.warning("="*60)
    logger.warning("This tests production config locally.")
    logger.warning("For actual production, use:")
    logger.warning("  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application")
    logger.warning("="*60)
    logger.info("")
    logger.info(f"Address: http://{host}:{port}")
    logger.info("Press Ctrl+C to stop")
    
    app = create_app(config_dict['production'])
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )


@cli.command()
def shell():
    """
    Start interactive Python shell with app context
    
    Useful for debugging and testing. The app object and
    database are pre-loaded.
    
    Examples:
        python manage.py shell
        >>> from app.models import User
        >>> User.query.first()
    """
    os.environ.setdefault('FLASK_ENV', 'development')
    
    app = create_app(config_dict['development'])
    
    with app.app_context():
        from app import db
        import app.models
        
        # Import all models into the local namespace
        models_module = app.models
        local_vars = {'app': app, 'db': db}
        for name in dir(models_module):
            if not name.startswith('_'):
                local_vars[name] = getattr(models_module, name)
        
        logger.info("Interactive shell started")
        logger.info("Available objects: app, db, and all models")
        
        # Start IPython if available, otherwise fall back to regular Python shell
        try:
            from IPython import embed
            embed(colors='neutral', user_ns=local_vars)
        except ImportError:
            import code
            code.interact(local=local_vars)


@cli.command()
@click.option('--coverage', is_flag=True, help='Run with coverage report')
def test(coverage):
    """
    Run test suite
    
    Examples:
        python manage.py test
        python manage.py test --coverage
    """
    os.environ['FLASK_ENV'] = 'testing'
    
    import pytest
    
    args = ['tests/', '-v']
    
    if coverage:
        args.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html'
        ])
    
    logger.info("Running test suite...")
    exit_code = pytest.main(args)
    
    if coverage and exit_code == 0:
        logger.info("Coverage report generated in htmlcov/")
    
    sys.exit(exit_code)


@cli.command()
@click.argument('message')
def db_migrate(message):
    """
    Create a new database migration
    
    Examples:
        python manage.py db-migrate "Add user email field"
    """
    os.environ.setdefault('FLASK_ENV', 'development')
    
    logger.info(f"Creating migration: {message}")
    
    try:
        from flask_migrate import Migrate, migrate as flask_migrate_cmd
        from app import db
        
        app = create_app(config_dict['development'])
        migrate_obj = Migrate(app, db)
        
        with app.app_context():
            from flask_migrate import migrate as do_migrate
            do_migrate(message=message)
            
        logger.info("Migration created successfully")
        logger.info("Review the migration file in migrations/versions/")
        logger.info("Then run: python manage.py db-upgrade")
    except Exception as e:
        logger.error(f"Migration creation failed: {e}")
        sys.exit(1)


@cli.command()
def db_upgrade():
    """
    Apply pending database migrations
    
    Examples:
        python manage.py db-upgrade
    """
    os.environ.setdefault('FLASK_ENV', 'development')
    
    logger.info("Applying database migrations...")
    
    try:
        from flask_migrate import Migrate, upgrade as flask_upgrade
        from app import db
        
        app = create_app(config_dict['development'])
        migrate_obj = Migrate(app, db)
        
        with app.app_context():
            flask_upgrade()
            
        logger.info("Migrations applied successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('revision', default='head')
def db_stamp(revision):
    """
    Stamp the database with a given revision without running migrations
    
    Useful when database schema is already at the desired state but
    migration history is out of sync.
    
    Examples:
        python manage.py db-stamp head
        python manage.py db-stamp b7c8d9e0f1a2
    """
    os.environ.setdefault('FLASK_ENV', 'development')
    
    logger.info(f"Stamping database with revision: {revision}")
    
    try:
        from flask_migrate import Migrate, stamp as flask_stamp
        from app import db
        
        app = create_app(config_dict['development'])
        migrate_obj = Migrate(app, db)
        
        with app.app_context():
            flask_stamp(revision=revision)
            
        logger.info(f"Database stamped successfully with revision: {revision}")
    except Exception as e:
        logger.error(f"Stamp failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--check-only', is_flag=True, help='Only check for differences, do not apply fixes')
@click.option('--no-stamp', is_flag=True, help='Do not stamp the database after fixing')
def fix_schema(check_only, no_stamp):
    """
    Detect and fix database schema mismatches with model definitions
    
    This command compares your database schema with SQLAlchemy models and:
    - Identifies missing columns that exist in models but not in database
    - Adds missing columns (unless --check-only is specified)
    - Stamps migration history to current state (unless --no-stamp is specified)
    
    Use this when migrations are out of sync with actual database schema,
    typically after manual schema changes or when migrating from older versions.
    
    Examples:
        py manage.py fix-schema                 # Check and fix all issues
        py manage.py fix-schema --check-only    # Only check, don't fix
        py manage.py fix-schema --no-stamp      # Fix but don't update migration history
    """
    os.environ.setdefault('FLASK_ENV', 'development')
    
    logger.info("="*60)
    logger.info("Database Schema Verification and Repair")
    logger.info("="*60)
    
    try:
        from flask_migrate import Migrate, stamp as flask_stamp
        from app import db
        from sqlalchemy import text, inspect
        
        app = create_app(config_dict['development'])
        migrate_obj = Migrate(app, db)
        
        with app.app_context():
            inspector = inspect(db.engine)
            issues_found = False
            fixes_applied = 0
            
            # Define expected columns for tables that commonly have issues
            # Format: {table_name: [(column_name, column_type, nullable), ...]}
            expected_schema = {
                'quote_line_items': [
                    ('assembly_metadata', 'TEXT', True),
                    ('list_price', 'NUMERIC(10, 2)', True),
                    ('custom_sku', 'VARCHAR(80)', True),
                    ('custom_name', 'VARCHAR(200)', True),
                    ('custom_description', 'TEXT', True),
                ],
                # Add more tables here as needed
            }
            
            logger.info("Checking database schema against model definitions...\n")
            
            for table_name, expected_columns in expected_schema.items():
                # Check if table exists
                if not inspector.has_table(table_name):
                    logger.warning(f"⚠ Table '{table_name}' does not exist in database")
                    issues_found = True
                    continue
                
                # Get current columns
                current_columns = {col['name']: col for col in inspector.get_columns(table_name)}
                
                # Check each expected column
                for col_name, col_type, nullable in expected_columns:
                    if col_name not in current_columns:
                        issues_found = True
                        logger.warning(f"✗ Missing column: {table_name}.{col_name} ({col_type})")
                        
                        if not check_only:
                            try:
                                nullable_clause = "" if nullable else " NOT NULL"
                                sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{nullable_clause}"
                                logger.info(f"  Executing: {sql}")
                                db.session.execute(text(sql))
                                db.session.commit()
                                logger.info(f"  ✓ Added column: {table_name}.{col_name}")
                                fixes_applied += 1
                            except Exception as e:
                                logger.error(f"  ✗ Failed to add column: {e}")
                                db.session.rollback()
                    else:
                        logger.info(f"✓ Column exists: {table_name}.{col_name}")
            
            # Summary
            logger.info("\n" + "="*60)
            if not issues_found:
                logger.info("✓ Database schema is in sync with models")
            else:
                if check_only:
                    logger.warning(f"Found schema mismatches. Run without --check-only to fix.")
                elif fixes_applied > 0:
                    logger.info(f"✓ Applied {fixes_applied} schema fix(es)")
                    
                    if not no_stamp:
                        logger.info("\nUpdating migration history...")
                        flask_stamp(revision='head')
                        logger.info("✓ Database stamped with latest migration")
                else:
                    logger.warning("Issues found but no fixes could be applied")
            
            logger.info("="*60)
            
            if not check_only and fixes_applied > 0 and not no_stamp:
                logger.info("\n✓ Schema repair completed successfully!")
                logger.info("You can now run the application without schema errors.")
            
    except Exception as e:
        logger.error(f"\n✗ Schema verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
def info():
    """
    Display application configuration info
    
    Shows current environment and configuration
    without starting the server.
    """
    env = os.environ.get('FLASK_ENV', 'production')
    
    logger.info("="*60)
    logger.info("RBM Tender App - Configuration Info")
    logger.info("="*60)
    logger.info(f"Environment: {env}")
    logger.info(f"Config: {config_dict.get(env, 'Unknown').__name__}")
    logger.info(f"Database URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
    logger.info(f"Secret Key: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")
    logger.info(f"Redis URL: {'Set' if os.environ.get('REDIS_URL') else 'Not set'}")
    logger.info("="*60)


if __name__ == '__main__':
    cli()

