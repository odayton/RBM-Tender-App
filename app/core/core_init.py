import os
from flask import Flask
from pathlib import Path

from .core_config import config_dict
from .core_logging import logger as core_logger
from .core_security import security_manager
from .core_errors import register_error_handlers
from .core_events import event_manager
from .core_rate_limiting import create_rate_limiter, handle_rate_limit_exceeded
from .core_metrics import init_metrics
from .core_monitoring import init_monitoring
from .core_caching import advanced_cache
from .core_api_docs import init_api_docs
from .core_feature_flags import init_feature_flags
from .core_circuit_breaker import init_circuit_breakers
from .core_db_safety import init_database_safety
from .core_advanced_monitoring import init_advanced_monitoring
# Remove the problematic import at the top

class CoreInitializer:
    """Initializes the core components and extensions of the application."""
    
    def __init__(self, app: Flask, db, login_manager, migrate, csrf, limiter=None):
        self.app = app
        self.db = db
        self.login_manager = login_manager
        self.migrate = migrate
        self.csrf = csrf
        self.limiter = limiter

    def init_app(self):
        """Run all initialization methods in the correct order."""
        self.init_config()
        self._create_directories()
        self.init_logging()
        self.init_database()
        self.init_security()
        self.init_csrf()
        self.init_rate_limiting()
        self.init_events()
        self.init_monitoring()
        self.init_metrics()
        self.init_caching()
        self.init_api_docs()
        self.init_feature_flags()
        self.init_circuit_breakers()
        self.init_advanced_monitoring()
        self.init_error_handlers()
        
        # Initialize database safety after all other components are ready
        with self.app.app_context():
            from .core_db_safety import init_database_safety
            init_database_safety(self.db)
            core_logger.app_logger.info("Database Safety Manager Initialized.")

    def init_config(self):
        """Initialize configuration from environment."""
        # Only initialize config if it hasn't been set already
        if not hasattr(self.app, '_config_initialized'):
            config_name = os.getenv('FLASK_CONFIG', 'development')
            config_class = config_dict[config_name]
            self.app.config.from_object(config_class)
            config_instance = config_class()
            config_instance.init_app(self.app)
            self.app._config_initialized = True

    def init_logging(self):
        """Initialize application logging."""
        core_logger.init_app(self.app)
        core_logger.app_logger.info("Logging Initialized.")

    def init_database(self):
        """Initialize database components and Flask-Migrate."""
        self.db.init_app(self.app)
        self.migrate.init_app(self.app, self.db)
        
        core_logger.app_logger.info("Database and Migrations Initialized.")
        
        # Initialize backup system (simplified)
        try:
            # Try to import from scripts directory
            import sys
            scripts_path = Path(__file__).parent.parent.parent / 'scripts' / 'utils'
            if scripts_path.exists():
                sys.path.insert(0, str(scripts_path))
                from backup_manager import BackupManager
                
                backup_manager = BackupManager()
                backup_manager.auto_backup()
                core_logger.app_logger.info("Backup system initialized successfully.")
            else:
                core_logger.app_logger.info("Backup system not available - scripts/utils directory not found.")
        except Exception as e:
            core_logger.app_logger.warning(f"Backup system initialization failed: {e}")

    def init_security(self):
        """Initialize security components."""
        security_manager.init_app(self.app)
        core_logger.app_logger.info("Security Initialized.")

    def init_csrf(self):
        """Initialize CSRF protection."""
        self.csrf.init_app(self.app)
        core_logger.app_logger.info("CSRF Protection Initialized.")

    def init_rate_limiting(self):
        """Initialize rate limiting."""
        if self.limiter:
            self.limiter.init_app(self.app)
            # Register rate limit error handler
            self.app.register_error_handler(429, handle_rate_limit_exceeded)
            core_logger.app_logger.info("Rate Limiting Initialized.")
        else:
            core_logger.app_logger.warning("Rate Limiter not provided. Rate limiting disabled.")

    def init_events(self):
        """Initialize the event manager and load listeners."""
        event_manager.init_app(self.app)
        core_logger.app_logger.info("Event System Initialized.")

    def init_monitoring(self):
        """Initialize monitoring and health checks."""
        init_monitoring(self.app)
        core_logger.app_logger.info("Monitoring Initialized.")

    def init_metrics(self):
        """Initialize Prometheus metrics."""
        init_metrics(self.app)
        core_logger.app_logger.info("Metrics Initialized.")

    def init_caching(self):
        """Initialize advanced caching system."""
        advanced_cache.init_app(self.app)
        core_logger.app_logger.info("Advanced Caching Initialized.")

    def init_api_docs(self):
        """Initialize API documentation."""
        init_api_docs(self.app)
        core_logger.app_logger.info("API Documentation Initialized.")

    def init_feature_flags(self):
        """Initialize feature flags system."""
        init_feature_flags(self.app)
        core_logger.app_logger.info("Feature Flags Initialized.")

    def init_circuit_breakers(self):
        """Initialize circuit breakers system."""
        init_circuit_breakers()
        core_logger.app_logger.info("Circuit Breakers Initialized.")

    def init_advanced_monitoring(self):
        """Initialize advanced monitoring system."""
        init_advanced_monitoring(self.app, self.db)
        core_logger.app_logger.info("Advanced Monitoring Initialized.")

    def init_error_handlers(self):
        """Register application-wide error handlers."""
        register_error_handlers(self.app)
        core_logger.app_logger.info("Error Handlers Registered.")

    def _create_directories(self):
        """Create necessary instance folders for logs, uploads, etc."""
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