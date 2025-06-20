import os
from flask import Flask
from pathlib import Path

# Import the application config dictionary
from .core_config import config_dict

# Import the singleton instances of our core components
from .core_logging import logger as core_logger
from .core_security import security_manager
from .core_errors import register_error_handlers
from .core_events import event_manager
from .core_cache import cache_manager

class CoreInitializer:
    """Initializes the core components and extensions of the application."""
    
    def __init__(self, app: Flask, db, login_manager, migrate):
        self.app = app
        self.db = db
        self.login_manager = login_manager
        self.migrate = migrate

    def init_app(self):
        """Run all initialization methods in the correct order."""
        self.init_config()
        self._create_directories()
        self.init_logging()
        self.init_database()
        self.init_security()
        self.init_cache()
        self.init_events()
        self.init_error_handlers() # Register handlers last

    def init_config(self):
        """Initialize configuration from environment."""
        config_name = os.getenv('FLASK_CONFIG', 'development')
        self.app.config.from_object(config_dict[config_name])
        # Allow config class to perform post-load actions, like loading YAML
        config_dict[config_name].init_app(self.app)

    def init_logging(self):
        """Initialize application logging."""
        core_logger.init_app(self.app)
        core_logger.app_logger.info("Logging Initialized.")

    def init_database(self):
        """Initialize database components and Flask-Migrate."""
        self.db.init_app(self.app)
        self.migrate.init_app(self.app, self.db)
        # The old DatabaseManager no longer needs an init_app call.
        core_logger.app_logger.info("Database and Migrations Initialized.")

    def init_security(self):
        """Initialize security components."""
        security_manager.init_app(self.app)
        self.login_manager.init_app(self.app)
        core_logger.app_logger.info("Security Initialized.")
        
    def init_cache(self):
        """Initialize the cache manager."""
        cache_manager.init_app(self.app)
        core_logger.app_logger.info("Cache System Initialized.")

    def init_events(self):
        """Initialize the event manager and load listeners."""
        event_manager.init_app(self.app)
        core_logger.app_logger.info("Event System Initialized.")

    def init_error_handlers(self):
        """Register application-wide error handlers."""
        register_error_handlers(self.app)
        core_logger.app_logger.info("Error Handlers Registered.")

    def _create_directories(self):
        """Create necessary instance folders for logs, uploads, etc."""
        # This method is now the single source of truth for directory creation.
        required_paths = [
            self.app.instance_path,
            self.app.config.get('LOG_DIR'),
            self.app.config.get('UPLOAD_DIR'),
            self.app.config.get('EXPORT_DIR'),
            self.app.config.get('SESSION_FILE_DIR')
        ]
        for path in required_paths:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)