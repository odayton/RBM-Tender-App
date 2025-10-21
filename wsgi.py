#!/usr/bin/env python3
"""
WSGI Entry Point for RBM Tender App
Industry-standard application entry point

This file is used by:
- Production servers (Gunicorn, uWSGI)
- Development servers (Flask CLI)
- Testing frameworks
- Any WSGI-compatible server

Environment is controlled via FLASK_ENV environment variable:
- development: Local development with debug
- production: Production deployment
- testing: Test suite execution

Usage:
    # Development
    FLASK_ENV=development flask run
    
    # Production (Gunicorn)
    FLASK_ENV=production gunicorn wsgi:application
    
    # Testing
    FLASK_ENV=testing pytest
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_root / 'config' / '.env')

from app import create_app
from app.core.core_config import config_dict

# Configure logging before app creation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_config():
    """
    Determine configuration based on environment variables.
    
    Priority:
    1. FLASK_ENV environment variable
    2. FLASK_CONFIG environment variable (alternative)
    3. Default to 'production' for safety
    
    Returns:
        Configuration class for the current environment
    """
    env = os.environ.get('FLASK_ENV') or os.environ.get('FLASK_CONFIG', 'production')
    env = env.lower()
    
    # Validate environment
    if env not in config_dict:
        logger.warning(
            f"Invalid environment '{env}', falling back to production. "
            f"Valid options: {', '.join(config_dict.keys())}"
        )
        env = 'production'
    
    config_class = config_dict[env]
    
    # Log configuration (without sensitive data)
    logger.info(f"Starting application with {env} configuration")
    logger.info(f"Configuration class: {config_class.__name__}")
    
    # Security checks for production
    if env == 'production':
        required_vars = ['DATABASE_URL', 'SECRET_KEY']
        missing = [var for var in required_vars if not os.environ.get(var)]
        
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            raise RuntimeError(
                f"Production environment requires: {', '.join(required_vars)}"
            )
        
        # Validate SECRET_KEY strength
        secret_key = os.environ.get('SECRET_KEY', '')
        if len(secret_key) < 32:
            logger.error(f"SECRET_KEY too short: {len(secret_key)} characters (minimum: 32)")
            raise RuntimeError("SECRET_KEY must be at least 32 characters for production")
        
        # Warn if DEBUG is enabled
        if os.environ.get('FLASK_DEBUG') == '1':
            logger.critical("FLASK_DEBUG is enabled in production! This is a security risk!")
    
    return config_class

# Create the application instance
try:
    config_class = get_config()
    application = create_app(config_class)
    
    # Log successful initialization
    logger.info("Application initialized successfully")
    
    # In development, log useful information
    if application.config.get('DEBUG'):
        logger.info("Debug mode is enabled")
        logger.info("Auto-reloader will watch for file changes")
    
except Exception as e:
    logger.critical(f"Failed to initialize application: {e}", exc_info=True)
    raise

# Flask CLI support
app = application

if __name__ == "__main__":
    """
    Direct execution support (not recommended for production)
    
    This allows running the file directly for quick testing:
        python wsgi.py
    
    For production, use a proper WSGI server:
        gunicorn wsgi:application
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Run RBM Tender App')
    parser.add_argument(
        '--host',
        default=os.environ.get('HOST', '127.0.0.1'),
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.environ.get('PORT', 5000)),
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=application.config.get('DEBUG', False),
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Security warning for production
    if os.environ.get('FLASK_ENV') == 'production':
        logger.warning("="*60)
        logger.warning("Running Flask development server in production mode")
        logger.warning("This is NOT recommended for production deployment!")
        logger.warning("Use Gunicorn or uWSGI for production:")
        logger.warning("  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application")
        logger.warning("="*60)
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    application.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )
