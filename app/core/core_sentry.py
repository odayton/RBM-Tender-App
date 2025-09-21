"""
Sentry Integration Module - Error Tracking and Performance Monitoring
"""

import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from flask import request, g, current_app
from app.core.core_monitoring import CorrelationIDManager

def init_sentry(app):
    """Initialize Sentry for error tracking and performance monitoring."""
    
    # Get Sentry DSN from environment
    sentry_dsn = os.environ.get('SENTRY_DSN')
    
    if not sentry_dsn:
        app.logger.warning("SENTRY_DSN not set - Sentry integration disabled")
        return
    
    # Configure Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FlaskIntegration(
                transaction_style="url",
                traces_sample_rate=1.0 if app.debug else 0.1,
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        traces_sample_rate=1.0 if app.debug else 0.1,
        profiles_sample_rate=1.0 if app.debug else 0.1,
        environment=app.config.get('ENV', 'development'),
        release=os.environ.get('SENTRY_RELEASE', 'unknown'),
        before_send=before_send_filter,
        before_send_transaction=before_send_transaction_filter,
    )
    
    # Set user context
    @app.before_request
    def set_sentry_context():
        if hasattr(g, 'user') and g.user:
            sentry_sdk.set_user({
                "id": g.user.id,
                "username": g.user.username,
                "email": g.user.email,
                "role": g.user.role.value if hasattr(g.user.role, 'value') else str(g.user.role)
            })
        
        # Set correlation ID
        correlation_id = CorrelationIDManager.get_correlation_id()
        if correlation_id:
            sentry_sdk.set_tag("correlation_id", correlation_id)
        
        # Set request context
        sentry_sdk.set_context("request", {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Unknown')
        })

def before_send_filter(event, hint):
    """Filter events before sending to Sentry."""
    
    # Don't send certain types of errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Skip common Flask errors that aren't actionable
        if exc_type.__name__ in ['NotFound', 'MethodNotAllowed']:
            return None
        
        # Skip database connection errors in development
        if current_app.debug and 'connection' in str(exc_value).lower():
            return None
    
    # Add correlation ID to all events
    correlation_id = CorrelationIDManager.get_correlation_id()
    if correlation_id:
        event.setdefault('tags', {})['correlation_id'] = correlation_id
    
    # Add environment information
    event.setdefault('tags', {}).update({
        'environment': current_app.config.get('ENV', 'development'),
        'flask_debug': current_app.debug,
        'flask_testing': current_app.config.get('TESTING', False)
    })
    
    return event

def before_send_transaction_filter(event, hint):
    """Filter transactions before sending to Sentry."""
    
    # Add correlation ID to transactions
    correlation_id = CorrelationIDManager.get_correlation_id()
    if correlation_id:
        event.setdefault('tags', {})['correlation_id'] = correlation_id
    
    return event

def capture_exception(exception, **kwargs):
    """Capture an exception with additional context."""
    with sentry_sdk.push_scope() as scope:
        # Add correlation ID
        correlation_id = CorrelationIDManager.get_correlation_id()
        if correlation_id:
            scope.set_tag("correlation_id", correlation_id)
        
        # Add custom context
        for key, value in kwargs.items():
            scope.set_context(key, value)
        
        # Capture the exception
        sentry_sdk.capture_exception(exception)

def capture_message(message, level='info', **kwargs):
    """Capture a message with additional context."""
    with sentry_sdk.push_scope() as scope:
        # Add correlation ID
        correlation_id = CorrelationIDManager.get_correlation_id()
        if correlation_id:
            scope.set_tag("correlation_id", correlation_id)
        
        # Add custom context
        for key, value in kwargs.items():
            scope.set_context(key, value)
        
        # Capture the message
        sentry_sdk.capture_message(message, level=level)

def capture_business_event(event_type, **kwargs):
    """Capture business events for analytics."""
    with sentry_sdk.push_scope() as scope:
        # Add correlation ID
        correlation_id = CorrelationIDManager.get_correlation_id()
        if correlation_id:
            scope.set_tag("correlation_id", correlation_id)
        
        # Set event type
        scope.set_tag("event_type", event_type)
        
        # Add business context
        scope.set_context("business_event", kwargs)
        
        # Capture as breadcrumb for context
        sentry_sdk.add_breadcrumb(
            message=f"Business event: {event_type}",
            category="business",
            level="info",
            data=kwargs
        )

def capture_security_event(event_type, **kwargs):
    """Capture security events for monitoring."""
    with sentry_sdk.push_scope() as scope:
        # Add correlation ID
        correlation_id = CorrelationIDManager.get_correlation_id()
        if correlation_id:
            scope.set_tag("correlation_id", correlation_id)
        
        # Set event type
        scope.set_tag("event_type", "security")
        scope.set_tag("security_event_type", event_type)
        
        # Add security context
        scope.set_context("security_event", kwargs)
        
        # Capture as breadcrumb for context
        sentry_sdk.add_breadcrumb(
            message=f"Security event: {event_type}",
            category="security",
            level="warning",
            data=kwargs
        )
        
        # Also capture as message for immediate attention
        sentry_sdk.capture_message(
            f"Security event: {event_type}",
            level="warning"
        )

def capture_performance_metric(operation, duration_ms, **kwargs):
    """Capture performance metrics."""
    with sentry_sdk.push_scope() as scope:
        # Add correlation ID
        correlation_id = CorrelationIDManager.get_correlation_id()
        if correlation_id:
            scope.set_tag("correlation_id", correlation_id)
        
        # Set performance context
        scope.set_context("performance", {
            "operation": operation,
            "duration_ms": duration_ms,
            **kwargs
        })
        
        # Capture as breadcrumb for context
        sentry_sdk.add_breadcrumb(
            message=f"Performance: {operation} ({duration_ms}ms)",
            category="performance",
            level="info",
            data={"operation": operation, "duration_ms": duration_ms, **kwargs}
        )

def set_user_context(user):
    """Set user context for Sentry."""
    if user:
        sentry_sdk.set_user({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
        })
    else:
        sentry_sdk.set_user(None)

def set_custom_context(key, value):
    """Set custom context for Sentry."""
    sentry_sdk.set_context(key, value)

def add_breadcrumb(message, category='default', level='info', **data):
    """Add a breadcrumb for context."""
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data
    )

# Import logging for the LoggingIntegration
import logging

