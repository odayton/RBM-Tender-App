from flask import Flask
from .core.core_init import CoreInitializer
from .extensions import db, login_manager, migrate # Import the new migrate object

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Use the CoreInitializer to set up the application
    # The CoreInitializer will now also handle initializing migrate
    core_initializer = CoreInitializer(app, db, login_manager, migrate)
    core_initializer.init_app()

    with app.app_context():
        # Import and register blueprints from the 'features' directory
        from app.features.admin import admin_bp
        from app.features.deals import deals_bp
        from app.features.pumps import pumps_bp
        from app.features.main import main_bp
        from app.features.hydraulic import hydraulic_bp
        from app.features.hydronics import hydronics_bp
        from app.features.static_server import static_server_bp

        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(deals_bp, url_prefix='/deals')
        app.register_blueprint(pumps_bp, url_prefix='/pumps')
        app.register_blueprint(main_bp)
        app.register_blueprint(hydraulic_bp, url_prefix='/hydraulic')
        app.register_blueprint(hydronics_bp, url_prefix='/hydronics')
        app.register_blueprint(static_server_bp)

        return app