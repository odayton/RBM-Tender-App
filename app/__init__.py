from flask import Flask
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

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Initialize core services using your existing CoreInitializer structure
    core_initializer = CoreInitializer(app, db, login_manager, migrate, csrf)
    core_initializer.init_app()

    # --- Development-Only Auto-Login ---
    # This block will only be active when DEBUG is True (i.e., in development)
    if app.config.get('DEBUG'):
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
    # --- End of Auto-Login ---

    with app.app_context():
        # Import and register blueprints from the 'features' directory
        from app.features.admin import admin_bp
        from app.features.deals import deals_bp
        from app.features.hvac import hvac_bp
        from app.features.plumbing import plumbing_bp
        from app.features.hydronic_heating import hydronic_heating_bp
        from app.features.main import main_bp
        from app.features.static_server import static_server_bp

        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(deals_bp, url_prefix='/deals')
        app.register_blueprint(hvac_bp, url_prefix='/hvac')
        app.register_blueprint(plumbing_bp, url_prefix='/plumbing')
        app.register_blueprint(hydronic_heating_bp, url_prefix='/hydronic-heating')
        app.register_blueprint(main_bp)
        app.register_blueprint(static_server_bp)

    # Register the custom CLI commands with the app instance
    register_cli_commands(app)

    return app
