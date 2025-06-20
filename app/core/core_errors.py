from typing import Optional, Dict, Any
from http import HTTPStatus
import traceback
from datetime import datetime
from flask import jsonify, current_app, request, Flask
from .core_logging import logger # Use central app logger

class AppError(Exception):
    """Base application error class for consistent error handling."""
    
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'UNSPECIFIED_ERROR'
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        # The logging is now handled by the registered error handler.

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for JSON responses."""
        error_dict = {
            'status': 'error',
            'message': self.message,
            'error_code': self.error_code,
        }
        if self.details:
            error_dict['details'] = self.details
        
        # Optionally add debug information
        if current_app and current_app.debug:
            error_dict['debug_info'] = {
                'status_code': self.status_code,
                'timestamp': self.timestamp.isoformat()
            }
        return error_dict

    def to_response(self):
        """Convert the error to a Flask JSON response."""
        return jsonify(self.to_dict()), self.status_code

# --- Specific Error Subclasses ---

class ValidationError(AppError):
    """Indicates an error in user-provided data."""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details['field'] = field
        super().__init__(
            message=message, status_code=HTTPStatus.BAD_REQUEST,
            error_code='VALIDATION_ERROR', details=details
        )

class DatabaseError(AppError):
    """Indicates a database operation failure."""
    def __init__(self, message: str = "A database error occurred.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code='DATABASE_ERROR', details=details
        )

class AuthenticationError(AppError):
    """Indicates an authentication failure (e.g., invalid credentials)."""
    def __init__(self, message: str = "Authentication failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, status_code=HTTPStatus.UNAUTHORIZED,
            error_code='AUTHENTICATION_ERROR', details=details
        )

class AuthorizationError(AppError):
    """Indicates a permissions failure."""
    def __init__(self, message: str = "You do not have permission to perform this action.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, status_code=HTTPStatus.FORBIDDEN,
            error_code='AUTHORIZATION_ERROR', details=details
        )

class NotFoundError(AppError):
    """Indicates a requested resource was not found."""
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type.title()} not found.",
            status_code=HTTPStatus.NOT_FOUND,
            error_code='RESOURCE_NOT_FOUND',
            details={'resource_type': resource_type, 'resource_id': str(resource_id)}
        )

class ConfigurationError(AppError):
    """Indicates a server configuration error."""
    def __init__(self, setting: str, details: str):
        super().__init__(
            message=f"Server configuration error for '{setting}'.",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code='CONFIGURATION_ERROR',
            details={'setting': setting, 'details': details}
        )

class FileOperationError(AppError):
    """Indicates a file operation failure."""
    def __init__(self, operation: str, filename: str, details: str):
        super().__init__(
            message=f"File operation '{operation}' failed for '{filename}'.",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code='FILE_OPERATION_ERROR',
            details={'operation': operation, 'filename': filename, 'details': details}
        )

# --- Error Handler Registration ---

def register_error_handlers(app: Flask):
    """Registers custom error handlers with the Flask application."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        """Handle any custom AppError and log it."""
        logger.error(f"AppError Handled: {error.__class__.__name__} - {error.message}", extra=error.to_dict(), exc_info=True)
        return error.to_response()

    @app.errorhandler(404)
    def handle_404_error(error):
        """Handle standard 404 Not Found errors."""
        err = NotFoundError('page', request.path)
        logger.warning(f"404 Not Found: {request.method} {request.path}")
        return err.to_response()
    
    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle uncaught exceptions to prevent sensitive data leaks."""
        # This is a fallback for unexpected errors.
        # We log the actual exception but return a generic error message to the user.
        logger.critical(f"Unhandled Exception: {error}", exc_info=True)
        
        app_error = AppError(
            message="An unexpected internal server error occurred.",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code='UNHANDLED_EXCEPTION'
        )
        return app_error.to_response()