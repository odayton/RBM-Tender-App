from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Print the DATABASE_URL to confirm it is loaded correctly
print(DATABASE_URL)

from flask import Flask, render_template
from app.app_config import DevelopmentConfig, ProductionConfig
from app.app_extensions import db, csrf
from app.blueprints.admin.admin_module import admin
from app.blueprints.pumps.pump_module import pumps
from app.blueprints.quotes.quote_module import quotes
import os

def create_app(config_name=None):
    """
    Create and configure Flask application
    Args:
        config_name: Configuration to use (development/production)
    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Configure app
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Load instance config if it exists
    if os.path.exists(os.path.join(app.instance_path, 'instance_config.py')):
        app.config.from_pyfile('instance_config.py')

    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def init_extensions(app):
    """
    Initialize Flask extensions
    Args:
        app: Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()

def register_blueprints(app):
    """
    Register Flask blueprints
    Args:
        app: Flask application instance
    """
    # Register admin blueprint
    app.register_blueprint(admin, url_prefix='/admin')
    
    # Register pumps blueprint
    app.register_blueprint(pumps, url_prefix='/pumps')
    
    # Register quotes blueprint
    app.register_blueprint(quotes, url_prefix='/quotes')

def configure_logging(app):
    """
    Configure application logging
    Args:
        app: Flask application instance
    """
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Ensure log directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    
    # Set log format
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Set log level
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

def register_error_handlers(app):
    """
    Register error handlers
    Args:
        app: Flask application instance
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('layouts/error.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('layouts/error.html', error=error), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('layouts/error.html', error=error), 403

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('layouts/error.html', error=error), 400

# Global template filters
def register_template_filters(app):
    """
    Register global template filters
    Args:
        app: Flask application instance
    """
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('currency')
    def format_currency(value):
        if value is None:
            return '$0.00'
        return f'${value:,.2f}'

# Context processors
def register_context_processors(app):
    """
    Register context processors
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def utility_processor():
        def format_price(amount):
            return f'${amount:,.2f}' if amount else '$0.00'
        
        return dict(format_price=format_price)