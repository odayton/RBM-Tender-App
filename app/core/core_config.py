# app/core/core_config.py

from typing import Any, Dict, Optional
import os
from pathlib import Path
from datetime import timedelta
import yaml
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Configuration specific errors"""
    pass

class Config:
    """Base configuration class with core settings"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Basic Flask config
        self.SECRET_KEY = self._get_env('SECRET_KEY', 'dev-key-please-change')
        self.DEBUG = False
        self.TESTING = False
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-size
        
        # Database
        self.SQLALCHEMY_DATABASE_URI = self._get_env('DATABASE_URL')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_RECORD_QUERIES = True
        self.DATABASE_CONNECT_OPTIONS = {}
        
        # Paths configuration
        self.BASE_DIR = Path(__file__).parent.parent
        self.INSTANCE_PATH = self.BASE_DIR / 'instance'
        self.UPLOAD_FOLDER = self.INSTANCE_PATH / 'uploads'
        self.TECH_DATA_FOLDER = self.UPLOAD_FOLDER / 'tech-data'
        self.EXPORTS_FOLDER = self.INSTANCE_PATH / 'exports'
        self.LOGS_FOLDER = self.INSTANCE_PATH / 'logs'
        # FIX: Define SESSION_FILE_DIR before it is used in _create_directories
        self.SESSION_FILE_DIR = self.INSTANCE_PATH / 'sessions'
        
        # Ensure directories exist
        self._create_directories()
        
        # File upload settings
        self.ALLOWED_EXTENSIONS = {
            'pdf': ['pdf'],
            'excel': ['xlsx', 'xls'],
            'image': ['jpg', 'jpeg', 'png']
        }
        
        # Session configuration
        self.PERMANENT_SESSION_LIFETIME = timedelta(days=31)
        self.SESSION_TYPE = 'filesystem'
        # Note: The definition for SESSION_FILE_DIR was moved up
        
        # Cache configuration
        self.CACHE_TYPE = 'simple'
        self.CACHE_DEFAULT_TIMEOUT = 300
        self.CACHE_KEY_PREFIX = 'rbm_'
        self.CACHE_REDIS_URL = self._get_env('REDIS_URL', None)
        
        # Logging configuration
        self.LOG_LEVEL = self._get_env('LOG_LEVEL', 'INFO')
        self.LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.LOG_TO_STDOUT = self._get_env_bool('LOG_TO_STDOUT', False)
        
        # Email configuration
        self.MAIL_SERVER = self._get_env('MAIL_SERVER', 'localhost')
        self.MAIL_PORT = int(self._get_env('MAIL_PORT', 587))
        self.MAIL_USE_TLS = self._get_env_bool('MAIL_USE_TLS', True)
        self.MAIL_USERNAME = self._get_env('MAIL_USERNAME')
        self.MAIL_PASSWORD = self._get_env('MAIL_PASSWORD')
        
        # Application specific settings
        self.DEALS_PER_PAGE = 20
        self.PUMPS_PER_PAGE = 50
        self.SEARCH_RESULTS_PER_PAGE = 25
        
        # Security settings
        self.PASSWORD_MIN_LENGTH = 8
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOGIN_DISABLED = False

    def _get_env(self, key: str, default: Any = None) -> Any:
        """Get environment variable with optional default"""
        value = os.environ.get(key, default)
        if value is None and default is None:
            raise ConfigurationError(f"Required environment variable {key} not set")
        return value

    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def _create_directories(self) -> None:
        """Create necessary application directories"""
        directories = [
            self.INSTANCE_PATH,
            self.UPLOAD_FOLDER,
            self.TECH_DATA_FOLDER,
            self.EXPORTS_FOLDER,
            self.LOGS_FOLDER,
            self.SESSION_FILE_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def load_yaml_config(self, filename: str) -> None:
        """Load additional configuration from YAML file"""
        file_path = self.INSTANCE_PATH / filename
        if file_path.exists():
            with open(file_path) as f:
                yaml_config = yaml.safe_load(f)
                for key, value in yaml_config.items():
                    setattr(self, key, value)

class DevelopmentConfig(Config):
    """Development configuration"""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = self._get_env(
            'DEV_DATABASE_URL',
            f'sqlite:///{self.INSTANCE_PATH}/dev.db'
        )
        self.CACHE_TYPE = 'simple'
        self.LOG_LEVEL = 'DEBUG'
        self.MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB for development

class ProductionConfig(Config):
    """Production configuration"""
    
    def __init__(self):
        super().__init__()
        # Security settings
        self.SESSION_COOKIE_SECURE = True
        self.REMEMBER_COOKIE_SECURE = True
        self.SESSION_COOKIE_HTTPONLY = True
        self.REMEMBER_COOKIE_HTTPONLY = True
        
        # Use Redis for caching in production
        self.CACHE_TYPE = 'redis'
        
        # Stricter file upload limits
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB for production

class TestingConfig(Config):
    """Testing configuration"""
    
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = False
        self.SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database
        self.WTF_CSRF_ENABLED = False
        self.CACHE_TYPE = 'null'
        self.MAIL_SUPPRESS_SEND = True

def get_config(env: Optional[str] = None) -> Config:
    """Get configuration instance based on environment"""
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    env = env or os.environ.get('FLASK_ENV', 'development')
    config_class = configs.get(env, DevelopmentConfig)
    
    config = config_class()
    
    # Load additional configuration if available
    if env != 'testing':
        try:
            config.load_yaml_config('config.yaml')
        except Exception as e:
            logger.warning(f"Could not load YAML config: {e}")
    
    return config