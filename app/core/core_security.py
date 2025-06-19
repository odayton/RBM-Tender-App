# app/core/core_security.py

from typing import Optional, Dict, Any, List, Callable, Set
import secrets
from datetime import datetime, timedelta
import re
from functools import wraps
from flask import request, current_app, abort, session, g
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
import logging

from .core_errors import AuthenticationError, AuthorizationError
from .core_logging import core_logger

logger = logging.getLogger(__name__)

class SecurityManager:
    """Manages application security, authentication, and authorization"""
    
    def __init__(self, app=None):
        self.app = app
        self._blocked_ips: Dict[str, datetime] = {}
        self._login_attempts: Dict[str, int] = {}
        self._jwt_blacklist: Set[str] = set()
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Initialize security with the application"""
        self.app = app
        self._setup_security_headers()
        self._setup_request_handlers()
        self._cleanup_old_sessions()

    def _setup_security_headers(self) -> None:
        """Configure security headers"""
        @self.app.after_request
        def add_security_headers(response):
            response.headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'SAMEORIGIN',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': self._build_csp_policy(),
                'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
            })
            return response

    def _build_csp_policy(self) -> str:
        """Build Content Security Policy"""
        directives = {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com'],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", 'data:', 'blob:'],
            'font-src': ["'self'"],
            'connect-src': ["'self'"],
            'frame-ancestors': ["'none'"],
            'form-action': ["'self'"]
        }
        return '; '.join(f"{key} {' '.join(values)}" for key, values in directives.items())

    def _setup_request_handlers(self) -> None:
        """Set up request security handlers"""
        @self.app.before_request
        def security_checks():
            # Check for blocked IP
            if self._is_ip_blocked(request.remote_addr):
                core_logger.log_security_event(
                    'blocked_ip_request',
                    {'ip': request.remote_addr},
                    'warning'
                )
                abort(403)

            # CSRF protection for state-changing methods
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                token = session.get('_csrf_token')
                if not token or token != request.headers.get('X-CSRF-Token'):
                    abort(403)

            # Clean up expired blocks
            self._cleanup_blocked_ips()

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials
        
        Args:
            username: Username
            password: Password
        Returns:
            bool: Authentication success
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            user = self._get_user(username)
            if not user:
                self._record_failed_attempt(username)
                raise AuthenticationError("Invalid username or password")

            if not self.verify_password(user.password_hash, password):
                self._record_failed_attempt(username)
                raise AuthenticationError("Invalid username or password")

            self._reset_failed_attempts(username)
            self._update_last_login(user.id)
            
            return True

        except Exception as e:
            core_logger.log_security_event(
                'authentication_failed',
                {
                    'username': username,
                    'error': str(e)
                },
                'warning'
            )
            raise

    def generate_token(
        self,
        user_id: int,
        expires_in: int = 3600,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate JWT token"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow(),
                'sub': user_id,
                **(additional_claims or {})
            }
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise AuthenticationError("Failed to generate token")

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token
        
        Args:
            token: JWT token
        Returns:
            Dict: Token payload
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            if token in self._jwt_blacklist:
                raise AuthenticationError("Token has been blacklisted")

            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist"""
        self._jwt_blacklist.add(token)

    def _record_failed_attempt(self, identifier: str) -> None:
        """Record failed login attempt"""
        self._login_attempts[identifier] = self._login_attempts.get(identifier, 0) + 1
        
        if self._login_attempts[identifier] >= current_app.config['MAX_LOGIN_ATTEMPTS']:
            self._block_ip(request.remote_addr)

    def _block_ip(self, ip: str, duration: int = 3600) -> None:
        """Block an IP address"""
        self._blocked_ips[ip] = datetime.utcnow() + timedelta(seconds=duration)
        core_logger.log_security_event(
            'ip_blocked',
            {'ip': ip},
            'warning'
        )

    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        if ip in self._blocked_ips:
            if datetime.utcnow() < self._blocked_ips[ip]:
                return True
            del self._blocked_ips[ip]
        return False

    def _cleanup_blocked_ips(self) -> None:
        """Clean up expired IP blocks"""
        now = datetime.utcnow()
        self._blocked_ips = {
            ip: expiry 
            for ip, expiry in self._blocked_ips.items() 
            if expiry > now
        }

    def _cleanup_old_sessions(self) -> None:
        """Clean up expired sessions"""
        if hasattr(self.app, 'session_interface'):
            self.app.session_interface.cleanup()

# Security decorators
def login_required(f: Callable) -> Callable:
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated

def roles_required(*roles: str) -> Callable:
    """Decorator to require specific roles"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not any(current_user.has_role(role) for role in roles):
                raise AuthorizationError(
                    f"Required roles: {', '.join(roles)}"
                )
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_permissions(*permissions: str) -> Callable:
    """Decorator to require specific permissions"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not all(current_user.has_permission(perm) for perm in permissions):
                raise AuthorizationError(
                    f"Required permissions: {', '.join(permissions)}"
                )
            return f(*args, **kwargs)
        return decorated
    return decorator

# Create security manager instance
security_manager = SecurityManager()