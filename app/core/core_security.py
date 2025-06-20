from typing import Optional, Dict, Any, List, Callable, Set
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app, abort, session, g, Flask
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, UserMixin

from .core_errors import AuthenticationError, AuthorizationError
from .core_logging import logger # Use central app logger
from app.models import User # Import the User model
from app.extensions import db # Import the db session

class SecurityManager:
    """Manages application security, authentication, and authorization."""
    
    def __init__(self):
        self.app: Optional[Flask] = None
        self._blocked_ips: Dict[str, datetime] = {}
        self._login_attempts: Dict[str, int] = {}
        self._jwt_blacklist: Set[str] = set()

    def init_app(self, app: Flask) -> None:
        """Initialize security components with the Flask application."""
        self.app = app
        self._setup_security_headers()
        self._setup_request_handlers()
        logger.info("SecurityManager initialized.")

    def _setup_security_headers(self) -> None:
        """Configure security headers for all responses."""
        @self.app.after_request
        def add_security_headers(response):
            # These headers help protect against common web vulnerabilities.
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            # Force HTTPS
            if not self.app.debug:
                 response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            return response

    def _setup_request_handlers(self) -> None:
        """Set up security checks to run before each request."""
        @self.app.before_request
        def security_checks():
            # IP-based rate limiting check
            if self._is_ip_blocked(request.remote_addr):
                logger.app_logger.warning(f"Request denied from blocked IP: {request.remote_addr}")
                abort(403, "Your IP has been temporarily blocked due to suspicious activity.")
            
            # NOTE: CSRF protection is now expected to be handled by Flask-WTF on a per-form basis.
            # The global check has been removed as it's less flexible and secure.
            
            # Clean up expired IP blocks periodically
            self._cleanup_blocked_ips()

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticates user credentials against the database.
        Returns the User object on success, None on failure.
        """
        try:
            user = self._get_user_by_email(email)
            if not user or not self.verify_password(user.password, password):
                self._record_failed_attempt(email)
                logger.app_logger.warning(f"Failed login attempt for email: {email}")
                return None

            self._reset_failed_attempts(email)
            self._update_last_login(user)
            return user
        except Exception as e:
            logger.app_logger.error(f"Error during authentication for {email}: {e}", exc_info=True)
            return None

    def generate_token(self, user_id: int, expires_in_seconds: int = 3600) -> str:
        """Generates a JWT for a given user ID."""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(seconds=expires_in_seconds),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        except Exception as e:
            logger.app_logger.error(f"Error generating JWT: {e}", exc_info=True)
            raise AuthenticationError("Failed to generate authentication token.")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifies a JWT. Returns payload on success, None on failure."""
        try:
            if token in self._jwt_blacklist:
                raise AuthenticationError("Token has been revoked.")
            
            return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            logger.app_logger.info("Attempted to use an expired token.")
            return None
        except jwt.InvalidTokenError as e:
            logger.app_logger.warning(f"Invalid token used: {e}")
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password using a secure algorithm."""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Verifies a password against a stored hash."""
        return check_password_hash(password_hash, password)

    # --- Internal Helper Methods ---

    def _get_user_by_email(self, email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    def _update_last_login(self, user: User) -> None:
        try:
            user.last_login_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.app_logger.error(f"Failed to update last login time for user {user.id}: {e}", exc_info=True)

    def _record_failed_attempt(self, identifier: str):
        """Records a failed login attempt and blocks IP if threshold is exceeded."""
        with self._lock:
            self._login_attempts[identifier] = self._login_attempts.get(identifier, 0) + 1
            if self._login_attempts[identifier] >= self.app.config.get('MAX_LOGIN_ATTEMPTS', 5):
                self._block_ip(request.remote_addr)

    def _reset_failed_attempts(self, identifier: str):
        with self._lock:
            self._login_attempts.pop(identifier, None)

    def _block_ip(self, ip: str):
        block_duration = self.app.config.get('IP_BLOCK_DURATION_SECONDS', 3600)
        self._blocked_ips[ip] = datetime.utcnow() + timedelta(seconds=block_duration)
        logger.app_logger.critical(f"IP address blocked due to excessive failed logins: {ip}")

    def _is_ip_blocked(self, ip: str) -> bool:
        """Checks if an IP is currently blocked."""
        if expiry := self._blocked_ips.get(ip):
            if datetime.utcnow() < expiry:
                return True
            # Block has expired, remove it
            del self._blocked_ips[ip]
        return False

    def _cleanup_blocked_ips(self):
        """Periodically cleans up the expired IP block dictionary."""
        # A simple implementation; a real-world scenario might use a scheduled job.
        if secrets.randbelow(100) == 1: # Run roughly 1% of the time
            now = datetime.utcnow()
            with self._lock:
                expired_ips = [ip for ip, expiry in self._blocked_ips.items() if expiry < now]
                for ip in expired_ips:
                    del self._blocked_ips[ip]

# --- Authorization Decorators ---

def roles_required(*roles: str):
    """Decorator to require specific roles for a route."""
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            # Assumes current_user has a 'roles' attribute which is a list/set of role names
            user_roles = {role.name for role in getattr(current_user, 'roles', [])}
            if not set(roles).issubset(user_roles):
                logger.app_logger.warning(f"User {current_user.id} denied access to {request.path}. Required roles: {roles}, User roles: {user_roles}")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Global Instance ---
security_manager = SecurityManager()