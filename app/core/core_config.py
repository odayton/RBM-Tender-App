from typing import Any, Dict, Optional
import os
import secrets
from pathlib import Path
from datetime import timedelta
import yaml
from dotenv import load_dotenv
from app.core.core_logging import logger # Use central app logger
from app.core.core_secrets import secrets_manager, env_validator, validate_secrets

# Load environment variables from .env file in config directory
load_dotenv('config/.env')

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class Config:
    """Base configuration class with default settings."""
    
    # Core Flask settings - CRITICAL: Generate strong secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Generate a cryptographically secure secret key if not provided
        SECRET_KEY = secrets_manager.generate_secret_key(64)
        logger.warning("SECRET_KEY not set in environment. Generated temporary key. Set SECRET_KEY environment variable for production.")
    
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-size
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Base path configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Fix INSTANCE_PATH to be relative to the application root, not absolute
    INSTANCE_PATH = BASE_DIR / 'instance'
    
    # Application-specific paths (these will be used by CoreInitializer to create dirs)
    LOG_DIR = INSTANCE_PATH / 'logs'
    UPLOAD_DIR = INSTANCE_PATH / 'uploads'
    EXPORT_DIR = INSTANCE_PATH / 'exports'
    SESSION_FILE_DIR = INSTANCE_PATH / 'sessions'
    
    # Session configuration - SECURED for production
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Reduced from 31 days
    SESSION_COOKIE_SECURE = False  # Temporarily disabled for HTTP testing
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Cache configuration
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'rbm_cache:'
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Flask-WTF configuration
    WTF_I18N_ENABLED = False  # Disable internationalization to prevent app context issues

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Auto-login configuration (disabled by default)
    ENABLE_AUTO_LOGIN = False
    
    # Advanced monitoring configuration (can be disabled to prevent CPU issues)
    ENABLE_ADVANCED_MONITORING = os.environ.get('ENABLE_ADVANCED_MONITORING', 'true').lower() in ('true', '1', 'yes')
    
    # Security configuration
    SECURITY_MAX_LOGIN_ATTEMPTS = int(os.environ.get('SECURITY_MAX_LOGIN_ATTEMPTS', '10'))
    SECURITY_BLOCK_DURATION_MINUTES = int(os.environ.get('SECURITY_BLOCK_DURATION_MINUTES', '15'))
    
    def validate_environment(self):
        """Validate critical environment variables for production."""
        # Use our comprehensive secrets validation
        if not validate_secrets():
            validation_result = env_validator.validate_environment()
            missing_critical = validation_result.get('missing_critical', [])
            if missing_critical:
                raise ConfigurationError(f"Missing critical environment variables: {', '.join(missing_critical)}")
        
        # Additional environment-specific validation
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            if not os.environ.get('SECRET_KEY') or len(os.environ.get('SECRET_KEY', '')) < 32:
                raise ConfigurationError("SECRET_KEY must be at least 32 characters in production")
            if os.environ.get('DEBUG', '').lower() == 'true':
                raise ConfigurationError("DEBUG must be False in production")
    
    def init_app(self, app):
        """
        A hook for any post-configuration initialization.
        We also load an optional YAML file here for overrides.
        """
        # Validate environment variables - call the method on the actual config class
        self.validate_environment()
        
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
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = 'DEBUG'
    
    # PostgreSQL for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

    # Use a simpler cache for development
    CACHE_TYPE = 'SimpleCache'
    
    # Development-specific settings - SECURITY: Keep CSRF enabled for security testing
    WTF_CSRF_ENABLED = False  # Temporarily disabled for debugging
    WTF_I18N_ENABLED = False  # Disable internationalization to prevent app context issues
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    REMEMBER_COOKIE_SECURE = False  # Allow HTTP in development
    ENABLE_AUTO_LOGIN = False  # Disable auto-login for normal development
    
    def init_app(self, app):
        """Initialize development configuration with validation."""
        super().init_app(app)
        
        # Validate that DEV_DATABASE_URL is set for development
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ConfigurationError("DEV_DATABASE_URL must be set for development environment")

class ProductionConfig(Config):
    """Production-specific configuration."""
    # Ensure the DATABASE_URL is set for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Production security settings
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = False  # Temporarily disabled for debugging
    WTF_I18N_ENABLED = False  # Disable internationalization to prevent app context issues
    SESSION_COOKIE_SECURE = False  # Temporarily disabled for HTTP testing
    REMEMBER_COOKIE_SECURE = True
    
    # Use Redis for caching in production
    CACHE_TYPE = 'RedisCache'
    if not Config.REDIS_URL:
        logger.warning("REDIS_URL is not set for production. Caching will fall back to in-memory.")
        CACHE_TYPE = 'SimpleCache'
    
    def init_app(self, app):
        """Initialize production configuration with validation."""
        super().init_app(app)
        
        # Force debug mode to False in production
        app.config['DEBUG'] = False
        
        # Validate that DATABASE_URL is set for production
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ConfigurationError("DATABASE_URL must be set for production environment")
        
        # Additional production security checks
        if app.config.get('DEBUG'):
            logger.warning("DEBUG mode is enabled in production! This is a security risk.")
            app.config['DEBUG'] = False
        
        if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'a-very-secret-key-that-you-should-change':
            raise ConfigurationError("SECRET_KEY must be set to a secure value in production.")


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    # Use PostgreSQL for testing - prioritize TEST_DATABASE_URL, fallback to DEV_DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or os.environ.get('DEV_DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # Final fallback to default test database URL
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:MadeInItaly1953!@localhost:5432/rbm_tender_app_test'
    
    WTF_CSRF_ENABLED = False # Disable CSRF forms in tests
    CACHE_TYPE = 'NullCache' # Disable caching for tests
    ENABLE_AUTO_LOGIN = False  # Disable auto-login for testing
    # Use environment variable for test secret key, fallback to generated key
    SECRET_KEY = os.environ.get('TEST_SECRET_KEY', secrets_manager.generate_secret_key(32))
    LOG_LEVEL = 'WARNING'  # Reduce log noise during testing
    
    def validate_environment(self):
        """Skip environment validation for testing."""
        # Testing doesn't require environment validation
        pass


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