from typing import Optional, Dict, Any
from flask import Flask, current_app, request
import logging
import os
from datetime import datetime

print("--- LOADING LATEST VERSION OF core_init.py ---")

from ..app_extensions import db, csrf, session
from ..app_logging import app_logger

logger = logging.getLogger(__name__)

class CoreInitializer:
    """Handles core application initialization and setup"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize core application components
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self._init_directories()
        self._init_database()
        self._init_logging()
        self._register_error_handlers()
        self._register_before_request()
        self._register_after_request()
        self._register_teardown()
        
        logger.info("Core initialization completed successfully")

    def _init_directories(self) -> None:
        """Create necessary application directories"""
        try:
            directories = [
                self.app.config['INSTANCE_PATH'],
                self.app.config['UPLOAD_FOLDER'],
                self.app.config['TECH_DATA_FOLDER'],
                self.app.config['EXPORTS_FOLDER'],
                self.app.config['LOGS_FOLDER'],
                self.app.config['SESSION_FILE_DIR']
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Ensured directory exists: {directory}")
                
        except KeyError as e:
            logger.error(f"Failed to create directories: Configuration key not found - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create directories: {str(e)}")
            raise

    def _init_database(self) -> None:
        """Initialize database connection and tables"""
        try:
            db.init_app(self.app)
            with self.app.app_context():
                db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    def _init_logging(self) -> None:
        """Configure application logging"""
        logger.info("Logging initialized successfully")

    def _register_error_handlers(self) -> None:
        """Register application error handlers"""
        
        @self.app.errorhandler(404)
        def not_found_error(error):
            app_logger.log_error(error, {'path': request.path})
            return 'Not Found', 404

        @self.app.errorhandler(500)
        def internal_error(error):
            app_logger.log_error(error, {'path': request.path})
            return 'Internal Server Error', 500

        @self.app.errorhandler(403)
        def forbidden_error(error):
            app_logger.log_error(error, {'path': request.path})
            return 'Forbidden', 403

    def _register_before_request(self) -> None:
        """Register functions to run before each request"""
        
        @self.app.before_request
        def before_request():
            if self.app.config.get('MAINTENANCE_MODE', False):
                return 'Site is under maintenance', 503
                
            setattr(current_app, 'request_start_time', datetime.now())

    def _register_after_request(self) -> None:
        """Register functions to run after each request"""
        
        @self.app.after_request
        def after_request(response):
            start_time = getattr(current_app, 'request_start_time', None)
            if start_time:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                app_logger.log_access(
                    endpoint=request.endpoint,
                    method=request.method,
                    ip=request.remote_addr,
                    duration=duration
                )
            
            return response

    def _register_teardown(self) -> None:
        """Register application teardown functions"""
        
        @self.app.teardown_appcontext
        def shutdown_session(exception=None):
            db.session.remove()

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check health status of core components
        
        Returns:
            Dict containing health status of various components
        """
        health_status = {
            'database': True,
            'file_system': True,
            'logging': True
        }
        
        try:
            with self.app.app_context():
                db.session.execute('SELECT 1')
        except Exception as e:
            health_status['database'] = False
            logger.error(f"Database health check failed: {str(e)}")
        
        try:
            test_file = os.path.join(self.app.config['LOGS_FOLDER'], 'health_check_test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            health_status['file_system'] = False
            logger.error(f"File system health check failed: {str(e)}")
        
        try:
            logger.info("Health check test log")
        except Exception as e:
            health_status['logging'] = False
            logger.error(f"Logging health check failed: {str(e)}")
        
        return health_status

core_initializer = CoreInitializer()