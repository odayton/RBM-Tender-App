from flask import Flask
from app.core.core_config import get_config
from app.core.core_init import core_initializer
from app.app_extensions import db, csrf, session, cache, mail
import os

# Import all the new, refactored blueprint packages
from app.features.main import main_bp
from app.features.deals import deals_bp
from app.features.admin import admin_bp
from app.features.pumps import pumps_bp
from app.features.hydraulic import hydraulic_bp
from app.features.hydronics import hydronics_bp

def create_app(config_name=None):
    """Application factory function"""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize core components
    core_initializer.init_app(app)

    # Initialize extensions
    csrf.init_app(app)
    session.init_app(app)
    cache.init_app(app)
    mail.init_app(app)

    # Register all blueprints directly
    app.register_blueprint(main_bp)
    app.register_blueprint(deals_bp, url_prefix='/deals')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(pumps_bp, url_prefix='/pumps')
    app.register_blueprint(hydraulic_bp, url_prefix='/hydraulic')
    app.register_blueprint(hydronics_bp, url_prefix='/hydronics')

    return app