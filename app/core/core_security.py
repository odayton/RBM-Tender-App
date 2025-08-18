import time
from datetime import datetime, timedelta
from flask import request, abort, current_app, g, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_login import LoginManager, current_user
from functools import wraps
import secrets
import re
from pathlib import Path

from app.models import User
from app.core.core_logging import logger

login_manager = LoginManager()

class SecurityManager:
    def __init__(self):
        self.app = None
        self.login_manager = login_manager
        self.failed_logins = {}
        self.blocked_ips = {}
        self.rate_limit_data = {}

    def init_app(self, app):
        self.app = app
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login' 

        # This function tells Flask-Login how to load a user from an ID.
        # It is essential for session management.
        @self.login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
            
        app.before_request(self.security_checks)
        app.after_request(self.add_security_headers)
        
        logger.info("SecurityManager initialized.")

    def _track_failed_login(self, ip_address):
        """Track failed login attempts for an IP address."""
        now = time.time()
        if ip_address not in self.failed_logins:
            self.failed_logins[ip_address] = []
        
        block_duration = self.app.config.get('SECURITY_BLOCK_DURATION_MINUTES', 15) * 60
        self.failed_logins[ip_address] = [t for t in self.failed_logins[ip_address] if now - t < block_duration]
        
        self.failed_logins[ip_address].append(now)

    def security_checks(self):
        """Perform security checks on each request."""
        ip_address = request.remote_addr
        
        if ip_address in self.blocked_ips and time.time() < self.blocked_ips[ip_address]:
            abort(429)

        self._cleanup_blocked_ips()
        
        # Additional security checks
        self._check_request_headers()
        self._validate_content_type()

    def _check_request_headers(self):
        """Check for suspicious request headers."""
        suspicious_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Forwarded-Host',
            'X-Forwarded-Proto'
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log suspicious headers but don't block (they might be legitimate)
                logger.warning(f"Suspicious header detected: {header} = {request.headers[header]}")

    def _validate_content_type(self):
        """Validate content type for POST requests."""
        if request.method == 'POST':
            content_type = request.headers.get('Content-Type', '')
            if not content_type.startswith(('application/x-www-form-urlencoded', 'multipart/form-data', 'application/json')):
                logger.warning(f"Invalid content type: {content_type}")

    def _cleanup_blocked_ips(self):
        """Periodically cleans up the blocked IPs dictionary."""
        if secrets.randbelow(100) == 1:
            now = time.time()
            self.blocked_ips = {ip: expiry for ip, expiry in self.blocked_ips.items() if expiry > now}

    def check_rate_limit(self, ip_address, endpoint=None, max_requests=10, window_seconds=60):
        """Enhanced rate limiting with endpoint-specific limits."""
        now = time.time()
        key = f"{ip_address}:{endpoint}" if endpoint else ip_address
        
        if key not in self.rate_limit_data:
            self.rate_limit_data[key] = []
        
        # Clean old entries
        self.rate_limit_data[key] = [t for t in self.rate_limit_data[key] if now - t < window_seconds]
        
        # Check if limit exceeded
        if len(self.rate_limit_data[key]) >= max_requests:
            return True
        
        # Add current request
        self.rate_limit_data[key].append(now)
        return False

    def check_login_rate_limit(self, ip_address):
        """Check if an IP has exceeded the login attempt limit."""
        max_attempts = self.app.config.get('SECURITY_MAX_LOGIN_ATTEMPTS', 10)
        if len(self.failed_logins.get(ip_address, [])) >= max_attempts:
            block_duration = self.app.config.get('SECURITY_BLOCK_DURATION_MINUTES', 15) * 60
            self.blocked_ips[ip_address] = time.time() + block_duration
            logger.warning(f"IP address {ip_address} has been blocked for {block_duration/60} minutes.")
            return True
        return False

    def generate_jwt(self, user_id, **kwargs):
        """Generate a JSON Web Token."""
        payload = {
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=1),
            'sub': user_id,
        }
        payload.update(kwargs)
        return jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256')

    def verify_jwt(self, token):
        """Verify a JSON Web Token."""
        try:
            payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def add_security_headers(self, response):
        """Add comprehensive security headers to the response."""
        # Basic security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Additional security headers
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (CSP) - Updated to include sortablejs and local scripts
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://cdnjs.cloudflare.com https://stackpath.bootstrapcdn.com https://cdn.jsdelivr.net https://*.jsdelivr.net https://jsdelivr.net https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https://ui-avatars.com; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        
        # HTTP Strict Transport Security (HSTS) - only in production
        if self.app.config.get('ENV') == 'production' or self.app.config.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Remove server information
        response.headers.pop('Server', None)
        
        return response

    def sanitize_input(self, data):
        """Sanitize user input to prevent XSS."""
        if isinstance(data, str):
            # Remove potentially dangerous characters
            data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
            data = re.sub(r'javascript:', '', data, flags=re.IGNORECASE)
            data = re.sub(r'on\w+\s*=', '', data, flags=re.IGNORECASE)
        return data

    def validate_file_upload(self, filename, allowed_extensions=None):
        """Validate file uploads for security."""
        if allowed_extensions is None:
            allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
        
        if not filename:
            return False, "No filename provided"
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return False, f"File type {file_ext} not allowed"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename"
        
        return True, "File upload valid"

# Global security manager instance
security_manager = SecurityManager()

def require_https(f):
    """Decorator to require HTTPS in production."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('ENV') == 'production':
            if not request.is_secure:
                abort(400, description="HTTPS required in production")
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=10, window_seconds=60):
    """Decorator to apply rate limiting to endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.remote_addr
            endpoint = request.endpoint
            
            if security_manager.check_rate_limit(ip_address, endpoint, max_requests, window_seconds):
                abort(429, description="Rate limit exceeded")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401, description="Authentication required")
        if not current_user.is_admin():
            abort(403, description="Admin privileges required")
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    """Decorator to require specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401, description="Authentication required")
            
            # Check if user has any of the required roles
            user_role = current_user.role.value if current_user.role else None
            if user_role not in roles:
                abort(403, description=f"Access denied. Required roles: {', '.join(roles)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator