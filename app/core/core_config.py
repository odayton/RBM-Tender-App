from typing import Any, Dict, Optional
import os
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
    
    # Core Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-size
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Base path configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_PATH = BASE_DIR / 'instance'
    
    # Application-specific paths (these will be used by CoreInitializer to create dirs)
    LOG_DIR = INSTANCE_PATH / 'logs'
    UPLOAD_DIR = INSTANCE_PATH / 'uploads'
    EXPORT_DIR = INSTANCE_PATH / 'exports'
    SESSION_FILE_DIR = INSTANCE_PATH / 'sessions'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Cache configuration
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'rbm_cache:'
    REDIS_URL = os.environ.get('REDIS_URL')

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    @staticmethod
    def init_app(app):
        """
        A hook for any post-configuration initialization.
        We also load an optional YAML file here for overrides.
        """
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

class ProductionConfig(Config):
    """Production-specific configuration."""
    # Ensure the DATABASE_URL is set for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ConfigurationError("DATABASE_URL must be set for production environment.")
    
    # Use Redis for caching in production
    CACHE_TYPE = 'RedisCache'
    if not Config.REDIS_URL:
        logger.warning("REDIS_URL is not set for production. Caching will fall back to in-memory.")
        CACHE_TYPE = 'SimpleCache'


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite database for tests
    WTF_CSRF_ENABLED = False # Disable CSRF forms in tests
    CACHE_TYPE = 'NullCache' # Disable caching for tests


# A dictionary to map configuration names to their classes
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}