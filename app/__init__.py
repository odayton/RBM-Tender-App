from flask import Flask
from .core.core_init import CoreInitializer
from .extensions import db, migrate, login_manager, csrf

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Pass the 'csrf' object to the initializer
    core_initializer = CoreInitializer(app, db, login_manager, migrate, csrf)
    core_initializer.init_app()

    with app.app_context():
        # Import and register blueprints from the 'features' directory
        from app.features.admin import admin_bp
        from app.features.deals import deals_bp
        # --- Corrected Imports and Blueprint Names ---
        from app.features.hvac import hvac_bp
        from app.features.plumbing import plumbing_bp
        from app.features.hydronic_heating import hydronic_heating_bp
        # ---
        from app.features.main import main_bp
        from app.features.static_server import static_server_bp

        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(deals_bp, url_prefix='/deals')
        # --- Corrected Blueprint Registrations ---
        app.register_blueprint(hvac_bp, url_prefix='/hvac')
        app.register_blueprint(plumbing_bp, url_prefix='/plumbing')
        app.register_blueprint(hydronic_heating_bp, url_prefix='/hydronic-heating')
        # ---
        app.register_blueprint(main_bp)
        app.register_blueprint(static_server_bp)

        return app