# app/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from .config import config
from .models import db
import os
from app.utils.db_utils.create_db import create_database, create_all_tables

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Use the config_name to get the appropriate configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Ensure the upload folders exist
    os.makedirs(app.config['TECH_DATA_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OTHER_UPLOADS_FOLDER'], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection

    with app.app_context():
        # Create the database and tables
        create_database()
        create_all_tables()

    # Register blueprints
    from app.blueprints.pumps import pumps_bp
    from app.blueprints.hydronics import hydronics_bp
    from app.blueprints.hydraulic import hydraulic_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.quotes import quotes_bp

    app.register_blueprint(pumps_bp, url_prefix='/pumps')
    app.register_blueprint(hydronics_bp, url_prefix='/hydronics')
    app.register_blueprint(hydraulic_bp, url_prefix='/hydraulic')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(quotes_bp, url_prefix='/quotes')

    @app.route('/')
    def home():
        return render_template('home.html', page_id='home')

    return app
