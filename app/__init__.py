import os
import time
from flask import Flask, request
from .core.core_init import CoreInitializer
from .core.core_logging import logger
from .extensions import db, migrate, login_manager, csrf

def register_cli_commands(app: Flask):
    """Register custom CLI commands for the Flask app."""
    
    @app.cli.command("seed-db")
    def seed_db_command():
        """Seeds the database with initial data."""
        # We import here to avoid circular dependencies
        from seed import seed_database
        with app.app_context():
            seed_database()
        logger.info("Database seeding completed from CLI.")

def register_template_filters(app: Flask):
    """Register custom template filters with the Flask app."""
    from .utils.view_helpers.template_helper import TemplateHelper
    from datetime import datetime
    
    @app.template_filter('format_date')
    def format_date_filter(value, format_str='%Y-%m-%d'):
        """Format date value for templates"""
        if value is None:
            return ''
        if isinstance(value, str) and value == "now":
            value = datetime.now()
        return TemplateHelper.format_date(value, format_str)
    
    @app.template_filter('format_date_dd_mm_yyyy')
    def format_date_dd_mm_yyyy_filter(value):
        """Format date value in dd-mm-yyyy format for templates"""
        if value is None:
            return ''
        if isinstance(value, str) and value == "now":
            value = datetime.now()
        return TemplateHelper.format_date_dd_mm_yyyy(value)
    
    @app.template_filter('add_months')
    def add_months_filter(value, months=1):
        """Add months to a date and return formatted string for templates"""
        return TemplateHelper.add_months_to_date(value, months)
    
    @app.template_filter('format_currency')
    def format_currency_filter(value):
        """Format currency value for templates"""
        if value is None or hasattr(value, '__class__') and value.__class__.__name__ == 'Undefined':
            return '$0.00'
        return TemplateHelper.format_currency(value)
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(value, format_str='%Y-%m-%d %H:%M:%S'):
        """Format datetime value for templates"""
        return TemplateHelper.format_datetime(value, format_str)
    
    @app.template_filter('nl2br')
    def nl2br_filter(value):
        """Convert newlines to HTML line breaks"""
        if value is None:
            return ''
        return value.replace('\n', '<br>')
    


def create_app(config_class=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, 
                instance_relative_config=True,
                static_folder='static',
                static_url_path='/static')
    
    # Load configuration
    if config_class:
        logger.info(f"Loading configuration from: {config_class.__name__}")
        app.config.from_object(config_class)
        # Call init_app if the config class has it
        if hasattr(config_class, 'init_app'):
            config_instance = config_class()
            config_instance.init_app(app)
            app._config_initialized = True
    else:
        # Check FLASK_CONFIG environment variable
        flask_config = os.environ.get('FLASK_CONFIG', 'development').lower()
        logger.info(f"FLASK_CONFIG environment variable: {flask_config}")
        
        if flask_config == 'testing':
            from .core.core_config import TestingConfig
            logger.info("Using TestingConfig from FLASK_CONFIG")
            app.config.from_object(TestingConfig)
            config_instance = TestingConfig()
            config_instance.init_app(app)
            app._config_initialized = True
        elif flask_config == 'production':
            from .core.core_config import ProductionConfig
            logger.info("Using ProductionConfig from FLASK_CONFIG")
            app.config.from_object(ProductionConfig)
            config_instance = ProductionConfig()
            config_instance.init_app(app)
            app._config_initialized = True
        else:
            # Default to development if no config specified
            from .core.core_config import DevelopmentConfig
            logger.info("No config specified, using default DevelopmentConfig")
            app.config.from_object(DevelopmentConfig)
            config_instance = DevelopmentConfig()
            config_instance.init_app(app)
            app._config_initialized = True
    
    # Ensure auto-login is explicitly set based on config class
    if config_class and hasattr(config_class, 'ENABLE_AUTO_LOGIN'):
        app.config['ENABLE_AUTO_LOGIN'] = config_class.ENABLE_AUTO_LOGIN
    
    # Check for environment variable override
    env_auto_login = os.environ.get('ENABLE_AUTO_LOGIN')
    if env_auto_login is not None:
        app.config['ENABLE_AUTO_LOGIN'] = env_auto_login.lower() in ('true', '1', 'yes')
    
    # Initialize core services using your existing CoreInitializer structure
    core_initializer = CoreInitializer(app, db, login_manager, migrate, csrf)
    core_initializer.init_app()
    
    # Initialize monitoring and error tracking
    from app.core.core_monitoring import init_monitoring
    from app.core.core_sentry import init_sentry
    
    init_monitoring(app)
    init_sentry(app)
    
    # Set application start time for uptime tracking
    app.config['START_TIME'] = time.time()

    # --- Development-Only Auto-Login ---
    # This block will only be active when ENABLE_AUTO_LOGIN is True
    auto_login_enabled = app.config.get('ENABLE_AUTO_LOGIN', False)
    
    if auto_login_enabled:
        @app.before_request
        def dev_auto_login():
            """
            For development convenience, automatically log in a default user 
            if no user is currently authenticated. This bypasses the need for a login page.
            """
            from flask_login import current_user, login_user
            from app.models import User
            
            # The app context is automatically available in a before_request handler
            if not current_user.is_authenticated:
                # This user must exist in the database, created by the seed script.
                dev_user = User.query.filter_by(email="dev@example.com").first()
                if dev_user:
                    login_user(dev_user, remember=True)
                    logger.info(f"Auto-logged in as {dev_user.email}")
                else:
                    logger.warning("Auto-login enabled but dev@example.com user not found in database")
            else:
                logger.debug(f"User already authenticated: {current_user.email}")
    else:
        logger.info("Auto-login is DISABLED - manual login required")
    # --- End of Auto-Login ---

    with app.app_context():
        # Import and register blueprints from the 'features' directory
        from app.features.auth import auth_bp
        from app.features.admin import admin_bp
        from app.features.deals import deals_bp
        from app.features.hvac import hvac_bp
        from app.features.plumbing import plumbing_bp
        from app.features.hydronic_heating import hydronic_heating_bp
        from app.features.main import main_bp
        from app.features.static_server import static_server_bp
        from app.features.crm import crm_bp
        from app.features.products import products_bp
        from app.features.monitoring import monitoring_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(deals_bp, url_prefix='/deals')
        app.register_blueprint(hvac_bp, url_prefix='/hvac')
        app.register_blueprint(plumbing_bp, url_prefix='/plumbing')
        app.register_blueprint(hydronic_heating_bp, url_prefix='/hydronic-heating')
        app.register_blueprint(main_bp)
        app.register_blueprint(static_server_bp)
        app.register_blueprint(crm_bp, url_prefix='/crm')
        app.register_blueprint(products_bp, url_prefix='/products')
        app.register_blueprint(monitoring_bp)

        # Register template filters
        register_template_filters(app)

    # Register the custom CLI commands with the app instance
    register_cli_commands(app)
    
    # Initialize migration manager
    from app.utils.db_utils.migration_manager import migration_manager
    migration_manager.init_app(app, db)
    
    # Register migration commands
    from app.commands.migration_commands import register_migration_commands
    register_migration_commands(app)
    
    # Register backup commands
    from app.commands.backup_commands import register_backup_commands
    register_backup_commands(app)

    return app
