import time
from datetime import datetime, timedelta
from flask import request, abort, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_login import LoginManager, current_user
from functools import wraps
import secrets

from app.models import User
from app.core.core_logging import logger

login_manager = LoginManager()

class SecurityManager:
    def __init__(self):
        self.app = None
        self.login_manager = login_manager
        self.failed_logins = {}
        self.blocked_ips = {}

    def init_app(self, app):
        self.app = app
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'main.home' 

        # This function tells Flask-Login how to load a user from an ID.
        # It is essential for session management.
        @self.login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
            
        app.before_request(self.security_checks)
        
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

    def _cleanup_blocked_ips(self):
        """Periodically cleans up the blocked IPs dictionary."""
        if secrets.randbelow(100) == 1:
            now = time.time()
            self.blocked_ips = {ip: expiry for ip, expiry in self.blocked_ips.items() if expiry > now}

    def check_rate_limit(self, ip_address):
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

    def set_security_headers(self, response):
        """Add security headers to the response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @staticmethod
    def roles_required(*roles):
        """Decorator to enforce role-based access control."""
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                if not current_user.is_authenticated or current_user.role.value not in roles:
                    abort(403)
                return fn(*args, **kwargs)
            return decorator
        return wrapper

security_manager = SecurityManager()