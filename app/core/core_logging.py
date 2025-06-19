# app/core/core_logging.py

from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
import logging.handlers
import json
from datetime import datetime
import threading
from functools import wraps
import time
import yaml
from flask import request, has_request_context

class RequestFormatter(logging.Formatter):
    """Custom formatter adding request info to logs"""
    
    def format(self, record):
        """Format log record with request information"""
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.request_id = request.headers.get('X-Request-ID', '')
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.request_id = None
            
        return super().format(record)

class CoreLogger:
    """Centralized logging management for the application"""
    
    def __init__(self, app=None):
        self.app = app
        self.loggers: Dict[str, logging.Logger] = {}
        self._log_dir = None
        self._config = None
        
        # Define standard formats
        self._formats = {
            'default': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            'detailed': ('%(asctime)s | %(levelname)s | %(name)s | '
                      '%(filename)s:%(lineno)d | %(message)s'),
            'request': ('%(asctime)s | %(levelname)s | %(remote_addr)s | '
                     '%(method)s %(url)s | %(message)s'),
            'security': ('%(asctime)s | SECURITY | %(levelname)s | '
                      '%(remote_addr)s | %(message)s'),
            'performance': ('%(asctime)s | PERFORMANCE | %(message)s | '
                        'Duration: %(duration).2fms')
        }
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Initialize logging with the application"""
        self.app = app
        self._log_dir = Path(app.config.get('LOG_DIR', 'logs'))
        self._load_config()
        self._setup_loggers()
        self._setup_request_logging()

    def _load_config(self) -> None:
        """Load logging configuration from YAML"""
        config_path = Path('logging_config.yaml')
        if config_path.exists():
            with open(config_path) as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = {
                'version': 1,
                'disable_existing_loggers': False,
                'root': {
                    'level': 'INFO'
                }
            }

    def _setup_loggers(self) -> None:
        """Set up all required loggers"""
        self._setup_app_logger()
        self._setup_request_logger()
        self._setup_security_logger()
        self._setup_performance_logger()
        self._setup_db_logger()
        self._setup_error_logger()

    def _setup_app_logger(self) -> None:
        """Set up main application logger"""
        logger = logging.getLogger('app')
        logger.setLevel(self.app.config.get('LOG_LEVEL', 'INFO'))
        
        # File handler
        handler = logging.handlers.RotatingFileHandler(
            self._log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        handler.setFormatter(logging.Formatter(self._formats['detailed']))
        logger.addHandler(handler)
        
        # Console handler in debug mode
        if self.app.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self._formats['default']))
            logger.addHandler(console_handler)
        
        self.loggers['app'] = logger

    def _setup_request_logger(self) -> None:
        """Set up request logging"""
        logger = logging.getLogger('request')
        handler = logging.handlers.TimedRotatingFileHandler(
            self._log_dir / 'requests.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        handler.setFormatter(RequestFormatter(self._formats['request']))
        logger.addHandler(handler)
        self.loggers['request'] = logger

    def _setup_security_logger(self) -> None:
        """Set up security event logging"""
        logger = logging.getLogger('security')
        handler = logging.handlers.TimedRotatingFileHandler(
            self._log_dir / 'security.log',
            when='midnight',
            interval=1,
            backupCount=90
        )
        handler.setFormatter(logging.Formatter(self._formats['security']))
        logger.addHandler(handler)
        self.loggers['security'] = logger

    def _setup_performance_logger(self) -> None:
        """Set up performance logging"""
        logger = logging.getLogger('performance')
        handler = logging.handlers.RotatingFileHandler(
            self._log_dir / 'performance.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(self._formats['performance']))
        logger.addHandler(handler)
        self.loggers['performance'] = logger

    def _setup_db_logger(self) -> None:
        """Set up database logging"""
        logger = logging.getLogger('db')
        handler = logging.handlers.RotatingFileHandler(
            self._log_dir / 'db.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(self._formats['detailed']))
        logger.addHandler(handler)
        self.loggers['db'] = logger

    def _setup_error_logger(self) -> None:
        """Set up error logging"""
        logger = logging.getLogger('error')
        handler = logging.handlers.RotatingFileHandler(
            self._log_dir / 'errors.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
        handler.setFormatter(logging.Formatter(self._formats['detailed']))
        logger.addHandler(handler)
        self.loggers['error'] = logger

    def _setup_request_logging(self) -> None:
        """Set up Flask request logging"""
        if not self.app:
            return

        @self.app.before_request
        def before_request():
            request.start_time = time.time()

        @self.app.after_request
        def after_request(response):
            if hasattr(request, 'start_time'):
                duration = (time.time() - request.start_time) * 1000
                self.log_request(
                    response.status_code,
                    duration
                )
            return response

    def log_request(self, status_code: int, duration: float) -> None:
        """Log HTTP request"""
        logger = self.loggers.get('request')
        if logger:
            logger.info(
                f"Status: {status_code}, Duration: {duration:.2f}ms",
                extra={
                    'status_code': status_code,
                    'duration': duration
                }
            )

    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = 'info'
    ) -> None:
        """Log security event"""
        logger = self.loggers.get('security')
        if logger:
            log_data = {
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'details': details
            }
            getattr(logger, severity.lower())(json.dumps(log_data))

    def log_performance(
        self,
        operation: str,
        duration: float,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log performance metric"""
        logger = self.loggers.get('performance')
        if logger:
            logger.info(
                f"{operation} completed",
                extra={
                    'duration': duration,
                    'context': context or {}
                }
            )

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error with context"""
        logger = self.loggers.get('error')
        if logger:
            log_data = {
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'timestamp': datetime.utcnow().isoformat(),
                'context': context or {}
            }
            logger.error(json.dumps(log_data), exc_info=True)

    def performance_monitor(self, operation_name: str):
        """Decorator to monitor function performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    self.log_performance(
                        operation_name,
                        duration,
                        {'success': True}
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    self.log_performance(
                        operation_name,
                        duration,
                        {
                            'success': False,
                            'error': str(e)
                        }
                    )
                    raise
            return wrapper
        return decorator

# Create global logger instance
core_logger = CoreLogger()

# Convenience functions and decorators
def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Convenience function for error logging"""
    core_logger.log_error(error, context)

def log_security(
    event_type: str,
    details: Dict[str, Any],
    severity: str = 'info'
) -> None:
    """Convenience function for security logging"""
    core_logger.log_security_event(event_type, details, severity)

def monitor_performance(operation_name: str):
    """Convenience decorator for performance monitoring"""
    return core_logger.performance_monitor(operation_name)