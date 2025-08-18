from typing import Any, Dict, Optional
import os
import secrets
from pathlib import Path
from datetime import timedelta
import yaml
from dotenv import load_dotenv
from app.core.core_logging import logger # Use central app logger

# Load environment variables from .env file at the module level
load_dotenv()

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class Config:
    """Base configuration class with default settings."""
    
    # Core Flask settings - CRITICAL: Generate strong secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Generate a cryptographically secure secret key if not provided
        SECRET_KEY = secrets.token_urlsafe(32)
        logger.warning("SECRET_KEY not set in environment. Generated temporary key. Set SECRET_KEY environment variable for production.")
    
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-size
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Base path configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Fix INSTANCE_PATH to be relative to the application root (/app) not the core_config.py location
    INSTANCE_PATH = Path('/app/instance')
    
    # Application-specific paths (these will be used by CoreInitializer to create dirs)
    LOG_DIR = INSTANCE_PATH / 'logs'
    UPLOAD_DIR = INSTANCE_PATH / 'uploads'
    EXPORT_DIR = INSTANCE_PATH / 'exports'
    SESSION_FILE_DIR = INSTANCE_PATH / 'sessions'
    
    # Session configuration - SECURED for production
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Reduced from 31 days
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Cache configuration
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'rbm_cache:'
    REDIS_URL = os.environ.get('REDIS_URL')

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Auto-login configuration (disabled by default)
    ENABLE_AUTO_LOGIN = False
    
    # Security configuration
    SECURITY_MAX_LOGIN_ATTEMPTS = int(os.environ.get('SECURITY_MAX_LOGIN_ATTEMPTS', '10'))
    SECURITY_BLOCK_DURATION_MINUTES = int(os.environ.get('SECURITY_BLOCK_DURATION_MINUTES', '15'))
    
    @staticmethod
    def validate_environment():
        """Validate critical environment variables for production."""
        required_vars = []
        if os.environ.get('FLASK_ENV') == 'production':
            required_vars = ['DATABASE_URL', 'SECRET_KEY']
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ConfigurationError(f"Missing required environment variables for production: {', '.join(missing_vars)}")
    
    @staticmethod
    def init_app(app):
        """
        A hook for any post-configuration initialization.
        We also load an optional YAML file here for overrides.
        """
        # Validate environment variables
        Config.validate_environment()
        
        config_yaml_path = app.config.get('INSTANCE_PATH') / 'config.yaml'
        try:
            if config_yaml_path.exists():
                with open(config_yaml_path) as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        app.config.from_mapping(yaml_config)
                        logger.info("Loaded additional configuration from config.yaml")
        except Exception as e:
            logger.warning(f"Could not load or parse config.yaml: {e}", exc_info=True)


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # --- THIS IS THE UPDATED LINE ---
    # We are changing 'new_dev.db' to 'rbm_tender_app.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL', 
        f"sqlite:///{Config.INSTANCE_PATH / 'rbm_tender_app.db'}"
    )
    # ------------------------------------

    # Use a simpler cache for development
    CACHE_TYPE = 'SimpleCache'
    
    # Development-specific settings - SECURITY: Keep CSRF enabled for security testing
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    REMEMBER_COOKIE_SECURE = False  # Allow HTTP in development
    ENABLE_AUTO_LOGIN = False  # Disable auto-login for normal development

class ProductionConfig(Config):
    """Production-specific configuration."""
    # Ensure the DATABASE_URL is set for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Production security settings
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Use Redis for caching in production
    CACHE_TYPE = 'RedisCache'
    if not Config.REDIS_URL:
        logger.warning("REDIS_URL is not set for production. Caching will fall back to in-memory.")
        CACHE_TYPE = 'SimpleCache'
    
    @classmethod
    def init_app(cls, app):
        """Initialize production configuration with validation."""
        super().init_app(app)
        
        # Force debug mode to False in production
        app.config['DEBUG'] = False
        
        # Validate that DATABASE_URL is set for production
        if not cls.SQLALCHEMY_DATABASE_URI:
            logger.error("DATABASE_URL is not set for production environment. Falling back to SQLite.")
            # Use SQLite as fallback but with proper permissions
            cls.SQLALCHEMY_DATABASE_URI = f"sqlite:///{Config.INSTANCE_PATH / 'rbm_tender_app.db'}"
        
        # Additional production security checks
        if app.config.get('DEBUG'):
            logger.warning("DEBUG mode is enabled in production! This is a security risk.")
            app.config['DEBUG'] = False
        
        if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'a-very-secret-key-that-you-should-change':
            raise ConfigurationError("SECRET_KEY must be set to a secure value in production.")


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite database for tests
    WTF_CSRF_ENABLED = False # Disable CSRF forms in tests
    CACHE_TYPE = 'NullCache' # Disable caching for tests
    ENABLE_AUTO_LOGIN = False  # Disable auto-login for testing


class DevEasyConfig(DevelopmentConfig):
    """Development configuration with auto-login for easy testing."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    ENABLE_AUTO_LOGIN = True  # Custom flag for auto-login
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing


# A dictionary to map configuration names to their classes
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'dev-easy': DevEasyConfig
}