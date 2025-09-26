"""
Enhanced Rate Limiting Module for RBM Tender App

This module provides comprehensive rate limiting including:
- IP-based rate limiting
- User-based rate limiting
- Endpoint-specific limits
- Adaptive rate limiting
- Security-focused limits for sensitive operations
"""

import os
import time
from typing import Dict, Optional, Callable, Any
from functools import wraps
from flask import request, current_app, g, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core.core_logging import logger


class RateLimitConfig:
    """Configuration for rate limiting."""
    
    # Default rate limits (requests per minute)
    DEFAULT_LIMITS = {
        'general': '100/minute',
        'auth': '5/minute',
        'admin': '20/minute',
        'api': '60/minute',
        'upload': '10/minute',
        'password_reset': '3/hour',
        '2fa_setup': '2/hour',
        'login_attempts': '5/minute',
        'registration': '2/hour'
    }
    
    # Sensitive endpoints that need stricter limits
    SENSITIVE_ENDPOINTS = {
        '/auth/login': '5/minute',
        '/auth/register': '2/hour',
        '/auth/reset-password': '3/hour',
        '/auth/2fa/setup': '2/hour',
        '/auth/2fa/verify': '10/minute',
        '/admin/*': '20/minute',
        '/api/*': '60/minute'
    }
    
    # IP-based blocking thresholds
    IP_BLOCK_THRESHOLDS = {
        'max_failed_logins': 10,
        'max_requests_per_minute': 200,
        'block_duration_minutes': 60
    }


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on behavior patterns."""
    
    def __init__(self):
        self.suspicious_ips = set()
        self.blocked_ips = {}
        self.request_counts = {}
        self.failed_login_counts = {}
    
    def is_ip_suspicious(self, ip: str) -> bool:
        """Check if an IP address is exhibiting suspicious behavior."""
        return ip in self.suspicious_ips
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP address is currently blocked."""
        if ip in self.blocked_ips:
            block_time = self.blocked_ips[ip]
            if time.time() - block_time < RateLimitConfig.IP_BLOCK_THRESHOLDS['block_duration_minutes'] * 60:
                return True
            else:
                # Unblock expired IPs
                del self.blocked_ips[ip]
        return False
    
    def record_failed_login(self, ip: str):
        """Record a failed login attempt."""
        self.failed_login_counts[ip] = self.failed_login_counts.get(ip, 0) + 1
        
        if self.failed_login_counts[ip] >= RateLimitConfig.IP_BLOCK_THRESHOLDS['max_failed_logins']:
            self.block_ip(ip, "Too many failed login attempts")
    
    def record_request(self, ip: str):
        """Record a request for rate limiting."""
        current_time = time.time()
        minute_key = int(current_time // 60)
        
        if ip not in self.request_counts:
            self.request_counts[ip] = {}
        
        if minute_key not in self.request_counts[ip]:
            self.request_counts[ip][minute_key] = 0
        
        self.request_counts[ip][minute_key] += 1
        
        # Check if IP is making too many requests
        total_requests = sum(self.request_counts[ip].values())
        if total_requests > RateLimitConfig.IP_BLOCK_THRESHOLDS['max_requests_per_minute']:
            self.block_ip(ip, "Too many requests per minute")
    
    def block_ip(self, ip: str, reason: str):
        """Block an IP address."""
        self.blocked_ips[ip] = time.time()
        self.suspicious_ips.add(ip)
        logger.warning(f"IP {ip} blocked: {reason}")
    
    def get_rate_limit_for_ip(self, ip: str) -> str:
        """Get appropriate rate limit for an IP based on its behavior."""
        if self.is_ip_blocked(ip):
            return "0/minute"  # Completely blocked
        
        if self.is_ip_suspicious(ip):
            return "10/minute"  # Reduced limit for suspicious IPs
        
        return RateLimitConfig.DEFAULT_LIMITS['general']


class SecurityRateLimiter:
    """Security-focused rate limiter for sensitive operations."""
    
    def __init__(self, limiter: Limiter):
        self.limiter = limiter
        self.adaptive_limiter = AdaptiveRateLimiter()
        self._setup_security_limits()
    
    def _setup_security_limits(self):
        """Set up security-focused rate limits."""
        
        # Authentication endpoints
        @self.limiter.limit("5 per minute")
        def auth_endpoints():
            pass
        
        # Admin endpoints
        @self.limiter.limit("20 per minute")
        def admin_endpoints():
            pass
        
        # API endpoints
        @self.limiter.limit("60 per minute")
        def api_endpoints():
            pass
    
    def get_client_identifier(self) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get user ID if authenticated
        if hasattr(g, 'user') and g.user and hasattr(g.user, 'id'):
            return f"user:{g.user.id}"
        
        # Fall back to IP address
        return get_remote_address()
    
    def apply_security_limits(self, endpoint: str, limit: str):
        """Apply security-focused rate limits to an endpoint."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check if IP is blocked
                client_ip = get_remote_address()
                if self.adaptive_limiter.is_ip_blocked(client_ip):
                    logger.warning(f"Blocked IP {client_ip} attempted to access {endpoint}")
                    return jsonify({
                        'error': 'Access denied',
                        'message': 'Your IP address has been temporarily blocked due to suspicious activity'
                    }), 403
                
                # Record request for adaptive limiting
                self.adaptive_limiter.record_request(client_ip)
                
                # Apply Flask-Limiter limit
                return self.limiter.limit(limit)(f)(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def record_failed_login(self, ip: str):
        """Record a failed login attempt."""
        self.adaptive_limiter.record_failed_login(ip)
    
    def record_successful_login(self, ip: str):
        """Record a successful login (reset failed attempts)."""
        if ip in self.adaptive_limiter.failed_login_counts:
            del self.adaptive_limiter.failed_login_counts[ip]


def create_rate_limiter(app) -> SecurityRateLimiter:
    """Create and configure the rate limiter."""
    
    # Get Redis URL if available, otherwise use memory storage
    redis_url = os.environ.get('REDIS_URL')
    storage_uri = redis_url if redis_url else "memory://"
    
    # Create Flask-Limiter instance
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=[RateLimitConfig.DEFAULT_LIMITS['general']],
        headers_enabled=True
    )
    
    # Create security rate limiter
    security_limiter = SecurityRateLimiter(limiter)
    
    # Set up global rate limit handlers
    @limiter.request_filter
    def exempt_from_rate_limit():
        """Exempt certain requests from rate limiting."""
        # Exempt health checks and static files
        if request.endpoint in ['static', 'health_check']:
            return True
        
        # Exempt localhost in development
        if app.debug and request.remote_addr in ['127.0.0.1', 'localhost']:
            return True
        
        return False
    
    return security_limiter


# Rate limiting decorators for easy use
def rate_limit(limit: str):
    """Decorator for applying rate limits to endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = current_app.extensions.get('limiter')
            if limiter:
                return limiter.limit(limit)(f)(*args, **kwargs)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_rate_limit():
    """Rate limit for authentication endpoints."""
    return rate_limit(RateLimitConfig.DEFAULT_LIMITS['auth'])


def admin_rate_limit():
    """Rate limit for admin endpoints."""
    return rate_limit(RateLimitConfig.DEFAULT_LIMITS['admin'])


def api_rate_limit():
    """Rate limit for API endpoints."""
    return rate_limit(RateLimitConfig.DEFAULT_LIMITS['api'])


def sensitive_rate_limit(limit: str = "3/hour"):
    """Rate limit for sensitive operations."""
    return rate_limit(limit)


# Security-focused rate limiting
def security_rate_limit(endpoint_type: str = "general"):
    """Apply security-focused rate limiting."""
    limits = {
        'login': '5/minute',
        'registration': '2/hour',
        'password_reset': '3/hour',
        '2fa_setup': '2/hour',
        'admin': '20/minute',
        'api': '60/minute',
        'upload': '10/minute'
    }
    
    limit = limits.get(endpoint_type, RateLimitConfig.DEFAULT_LIMITS['general'])
    return rate_limit(limit)


# Rate limit error handler
def handle_rate_limit_exceeded(e):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded: {request.remote_addr} - {request.endpoint}")
    
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': getattr(e, 'retry_after', 60)
    }), 429


# Utility functions for monitoring
def get_rate_limit_status(ip: str) -> Dict[str, Any]:
    """Get rate limit status for an IP address."""
    limiter = current_app.extensions.get('limiter')
    if not limiter:
        return {'status': 'limiter_not_available'}
    
    # This would need to be implemented based on the specific limiter backend
    return {
        'ip': ip,
        'status': 'active',
        'limits': RateLimitConfig.DEFAULT_LIMITS
    }


def reset_rate_limits(ip: str):
    """Reset rate limits for an IP address (admin function)."""
    limiter = current_app.extensions.get('limiter')
    if limiter and hasattr(limiter, 'reset'):
        limiter.reset(ip)
        logger.info(f"Rate limits reset for IP: {ip}")
        return True
    return False






