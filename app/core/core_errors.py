# app/core/core_errors.py

from typing import Optional, Dict, Any
from http import HTTPStatus
import logging
import traceback
from datetime import datetime
from flask import jsonify, current_app, request

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error class"""
    
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.source = source
        self.timestamp = datetime.utcnow()
        
        self._log_error()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format"""
        error_dict = {
            'status': 'error',
            'message': self.message,
            'error_code': self.error_code,
            'status_code': self.status_code,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
        if current_app.debug and self.source:
            error_dict['source'] = self.source
        return error_dict

    def to_response(self):
        """Convert error to HTTP response"""
        return jsonify(self.to_dict()), self.status_code

    def _log_error(self):
        """Log error details"""
        log_data = {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'status_code': self.status_code,
            'error_code': self.error_code,
            'details': self.details,
            'source': self.source,
            'stack_trace': traceback.format_exc()
        }
        logger.error(f"Application error occurred", extra=log_data)

class ValidationError(AppError):
    """Validation error"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ):
        details = details or {}
        if field:
            details['field'] = field
        
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code='VALIDATION_ERROR',
            details=details,
            source=source
        )

class DatabaseError(AppError):
    """Database operation error"""
    
    def __init__(
        self,
        operation: str,
        details: str,
        error_code: Optional[str] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"Database {operation} failed: {details}",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code=error_code or 'DATABASE_ERROR',
            details={'operation': operation},
            source=source
        )

class AuthenticationError(AppError):
    """Authentication error"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code='AUTHENTICATION_ERROR',
            details=details,
            source=source
        )

class AuthorizationError(AppError):
    """Authorization error"""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            error_code='AUTHORIZATION_ERROR',
            details=details,
            source=source
        )

class NotFoundError(AppError):
    """Resource not found error"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"{resource_type} with id {resource_id} not found",
            status_code=HTTPStatus.NOT_FOUND,
            error_code='RESOURCE_NOT_FOUND',
            details={
                'resource_type': resource_type,
                'resource_id': str(resource_id),
                **(details or {})
            },
            source=source
        )

class ConfigurationError(AppError):
    """Configuration error"""
    
    def __init__(
        self,
        setting: str,
        details: str,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"Configuration error for {setting}: {details}",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code='CONFIGURATION_ERROR',
            details={'setting': setting},
            source=source
        )

class FileOperationError(AppError):
    """File operation error"""
    
    def __init__(
        self,
        operation: str,
        filename: str,
        details: str,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"File {operation} failed for {filename}: {details}",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code='FILE_OPERATION_ERROR',
            details={
                'operation': operation,
                'filename': filename
            },
            source=source
        )

# Error handler registration
def register_error_handlers(app):
    """Register error handlers with Flask application"""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return error.to_response()

    @app.errorhandler(404)
    def handle_404(error):
        return NotFoundError(
            resource_type='page',
            resource_id=error.description,
            source='route_handler'
        ).to_response()

    @app.errorhandler(500)
    def handle_500(error):
        return AppError(
            message="Internal server error occurred",
            error_code='INTERNAL_SERVER_ERROR',
            source='system'
        ).to_response()

# Error checking decorators
def validate_request(schema):
    """Decorator to validate request data against schema"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                schema.validate(request.get_json())
            except ValidationError as e:
                raise ValidationError(
                    message="Invalid request data",
                    details=e.messages,
                    source=f.__name__
                )
            return f(*args, **kwargs)
        return wrapper
    return decorator

def handle_exceptions(f):
    """Decorator to handle exceptions in routes"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError:
            raise
        except Exception as e:
            logger.exception("Unhandled exception occurred")
            raise AppError(
                message="An unexpected error occurred",
                error_code='UNHANDLED_ERROR',
                details={'original_error': str(e)},
                source=f.__name__
            )
    return wrapper