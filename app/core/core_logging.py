from typing import Dict, Any, Optional
from pathlib import Path
import logging
import logging.config
import json
import time
import yaml
from flask import request, has_request_context, Flask

class RequestFormatter(logging.Formatter):
    """Custom formatter that adds request information to log records."""
    def format(self, record):
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
    """Centralized logging management for the application."""
    
    def __init__(self):
        self.app: Optional[Flask] = None
        self.loggers: Dict[str, logging.Logger] = {}
        self.default_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def init_app(self, app: Flask) -> None:
        """Initialize and configure logging for the Flask application."""
        self.app = app
        log_dir = Path(app.config.get('LOG_DIR', 'instance/logs'))
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging_config = self._get_logging_config(log_dir)
        logging.config.dictConfig(logging_config)

        for logger_name in logging_config.get('loggers', {}):
            self.loggers[logger_name] = logging.getLogger(logger_name)
        
        self._setup_request_logging()
        self.app_logger.info("CoreLogger initialized successfully.")

    def _get_logging_config(self, log_dir: Path) -> Dict[str, Any]:
        """Constructs the dictionary for logging.config.dictConfig."""
        log_level = self.app.config.get('LOG_LEVEL', 'INFO').upper()
        
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'},
                'detailed': {'format': '%(asctime)s [%(levelname)s] %(name)s %(module)s:%(lineno)d: %(message)s'},
                'request': {
                    '()': RequestFormatter,
                    'format': '%(asctime)s [%(levelname)s] %(remote_addr)s | %(method)s %(url)s | %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'level': log_level,
                    'stream': 'ext://sys.stdout'
                },
                'app_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'detailed',
                    'filename': log_dir / 'app.log',
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 10
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'detailed',
                    'filename': log_dir / 'errors.log',
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 10,
                    'level': 'ERROR'
                },
                 'request_file': {
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'formatter': 'request',
                    'filename': log_dir / 'requests.log',
                    'when': 'midnight',
                    'interval': 1,
                    'backupCount': 30
                }
            },
            'loggers': {
                'app': {
                    'handlers': ['console', 'app_file', 'error_file'] if self.app.debug else ['app_file', 'error_file'],
                    'level': log_level,
                    'propagate': False
                },
                'request': {
                    'handlers': ['request_file'],
                    'level': 'INFO',
                    'propagate': False
                }
            },
            'root': {
                'level': 'WARNING',
                'handlers': ['console', 'app_file']
            }
        }

    def _setup_request_logging(self):
        @self.app.before_request
        def before_request():
            request.start_time = time.time()

        @self.app.after_request
        def after_request(response):
            if hasattr(request, 'start_time'):
                duration_ms = (time.time() - request.start_time) * 1000
                self.request_logger.info(f"{response.status} | {duration_ms:.2f}ms")
            return response

    def debug(self, msg, *args, **kwargs):
        self.app_logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.app_logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.app_logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.app_logger.error(msg, *args, **kwargs)
        
    def exception(self, msg, *args, **kwargs):
        self.app_logger.exception(msg, *args, **kwargs)
    
    # Add the missing 'critical' method
    def critical(self, msg, *args, **kwargs):
        self.app_logger.critical(msg, *args, **kwargs)

    @property
    def app_logger(self) -> logging.Logger:
        return self.loggers.get('app', logging.getLogger('app'))

    @property
    def request_logger(self) -> logging.Logger:
        return self.loggers.get('request', logging.getLogger('request'))

logger = CoreLogger()