import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class AppLogger:
    def __init__(self):
        self.logger = logging.getLogger('app')
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # File handler
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)

    def log_system_event(self, level, message, extra=None):
        """Log a system event"""
        if hasattr(self.logger, level):
            log_func = getattr(self.logger, level)
            log_func(message, extra=extra)

    def log_db_query(self, query, duration):
        """Log a database query"""
        self.logger.debug(f"Query executed in {duration}ms: {query}")

    def log_access(self, endpoint, method, ip, duration):
        """Log an access request"""
        self.logger.info(
            f"Access: {method} {endpoint} from {ip} - Duration: {duration}ms"
        )

    def log_error(self, error, context=None):
        """Log an error"""
        self.logger.error(f"Error: {str(error)}", exc_info=True, extra=context)

# Create a global logger instance
app_logger = AppLogger()