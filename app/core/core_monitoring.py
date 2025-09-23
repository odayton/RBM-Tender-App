"""
Core Monitoring Module - Error Tracking, Logging, and Performance Monitoring
"""

import os
import time
import uuid
import logging
import structlog
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Dict, Any, Optional
from flask import request, g, current_app
from contextlib import contextmanager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation."""
        timer_id = str(uuid.uuid4())
        self.start_times[timer_id] = {
            'operation': operation,
            'start_time': time.time(),
            'timestamp': datetime.utcnow()
        }
        return timer_id
    
    def end_timer(self, timer_id: str, **kwargs) -> Dict[str, Any]:
        """End timing an operation and return metrics."""
        if timer_id not in self.start_times:
            logger.warning("Timer not found", timer_id=timer_id)
            return {}
        
        timer_data = self.start_times.pop(timer_id)
        duration = time.time() - timer_data['start_time']
        
        metrics = {
            'operation': timer_data['operation'],
            'duration_ms': round(duration * 1000, 2),
            'timestamp': timer_data['timestamp'].isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Log performance metrics
        logger.info("Performance metric", **metrics)
        
        # Store in metrics dict for aggregation
        operation = timer_data['operation']
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(metrics)
        
        return metrics
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        if operation not in self.metrics:
            return {}
        
        durations = [m['duration_ms'] for m in self.metrics[operation]]
        return {
            'operation': operation,
            'count': len(durations),
            'avg_duration_ms': round(sum(durations) / len(durations), 2),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'total_duration_ms': sum(durations)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations."""
        return {
            operation: self.get_operation_stats(operation)
            for operation in self.metrics.keys()
        }

class HealthChecker:
    """Health check system for monitoring application status."""
    
    def __init__(self):
        self.checks = {}
        self.last_check = None
    
    def register_check(self, name: str, check_func):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {
            'timestamp': datetime.now(datetime.timezone.utc).isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                check_result = check_func()
                duration = time.time() - start_time
                
                # Check if the result indicates unhealthy status
                if isinstance(check_result, dict) and check_result.get('status') == 'unhealthy':
                    results['checks'][name] = {
                        'status': 'unhealthy',
                        'duration_ms': round(duration * 1000, 2),
                        'result': check_result
                    }
                    results['overall_status'] = 'unhealthy'
                else:
                    results['checks'][name] = {
                        'status': 'healthy',
                        'duration_ms': round(duration * 1000, 2),
                        'result': check_result
                    }
            except Exception as e:
                logger.error("Health check failed", check_name=name, error=str(e))
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                results['overall_status'] = 'unhealthy'
        
        self.last_check = results
        return results
    
    def get_last_check(self) -> Optional[Dict[str, Any]]:
        """Get the last health check results."""
        return self.last_check

class CorrelationIDManager:
    """Manage correlation IDs for request tracing."""
    
    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a new correlation ID."""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get the current correlation ID from Flask's g object."""
        return getattr(g, 'correlation_id', None)
    
    @staticmethod
    def set_correlation_id(correlation_id: str):
        """Set the correlation ID in Flask's g object."""
        g.correlation_id = correlation_id

# Global instances
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()

def init_monitoring(app):
    """Initialize monitoring for the Flask app."""
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Register default health checks
    health_checker.register_check('database', check_database_health)
    health_checker.register_check('redis', check_redis_health)
    health_checker.register_check('disk_space', check_disk_space)
    
    # Add request logging middleware
    @app.before_request
    def before_request():
        # Generate correlation ID
        correlation_id = CorrelationIDManager.generate_correlation_id()
        CorrelationIDManager.set_correlation_id(correlation_id)
        
        # Start request timer
        g.request_start_time = time.time()
        
        # Log request start
        logger.info(
            "Request started",
            correlation_id=correlation_id,
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            
            # Log request completion
            try:
                response_size = len(response.get_data()) if hasattr(response, 'get_data') else 0
            except (RuntimeError, AttributeError):
                response_size = 0
                
            logger.info(
                "Request completed",
                correlation_id=CorrelationIDManager.get_correlation_id(),
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                response_size=response_size
            )
        
        return response

def performance_timer(operation_name: str):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timer_id = performance_monitor.start_timer(operation_name)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_timer(timer_id, success=True)
                return result
            except Exception as e:
                performance_monitor.end_timer(timer_id, success=False, error=str(e))
                raise
        return wrapper
    return decorator

@contextmanager
def performance_context(operation_name: str, **context):
    """Context manager for timing operations."""
    timer_id = performance_monitor.start_timer(operation_name)
    try:
        yield
        performance_monitor.end_timer(timer_id, success=True, **context)
    except Exception as e:
        performance_monitor.end_timer(timer_id, success=False, error=str(e), **context)
        raise

# Health check functions
def check_database_health():
    """Check database connectivity and performance."""
    try:
        from app.core.core_database import db
        from sqlalchemy import text
        
        # Test basic connectivity
        db.session.execute(text('SELECT 1'))
        
        # Test query performance
        start_time = time.time()
        db.session.execute(text('SELECT COUNT(*) FROM users'))
        duration = time.time() - start_time
        
        return {
            'status': 'healthy',
            'response_time_ms': round(duration * 1000, 2),
            'connection_pool_size': db.engine.pool.size(),
            'checked_out_connections': db.engine.pool.checkedout()
        }
    except Exception as e:
        # If database is not available, return unhealthy status
        return {
            'status': 'unhealthy',
            'error': str(e),
            'note': 'Database not available or not initialized'
        }

def check_redis_health():
    """Check Redis connectivity and performance."""
    try:
        from app.core.core_cache import cache_manager
        
        # Skip Redis check if cache manager is not properly initialized
        if not hasattr(cache_manager, 'app') or cache_manager.app is None:
            return {
                'status': 'healthy',
                'connection': 'in-memory fallback',
                'note': 'Redis not configured, using in-memory cache'
            }
        
        # Test basic connectivity
        test_key = f"health_check_{uuid.uuid4()}"
        cache_manager.set(test_key, "test_value", timeout=10)
        value = cache_manager.get(test_key)
        cache_manager.delete(test_key)
        
        if value != "test_value":
            raise Exception("Redis value mismatch")
        
        return {
            'status': 'healthy',
            'connection': 'active'
        }
    except Exception as e:
        raise Exception(f"Redis health check failed: {str(e)}")

def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        
        # Check disk space for the instance directory
        instance_path = os.path.join(os.getcwd(), 'instance')
        if not os.path.exists(instance_path):
            instance_path = os.getcwd()
        
        total, used, free = shutil.disk_usage(instance_path)
        free_percent = (free / total) * 100
        
        if free_percent < 10:
            raise Exception(f"Low disk space: {free_percent:.1f}% free")
        
        return {
            'status': 'healthy',
            'free_space_gb': round(free / (1024**3), 2),
            'free_percent': round(free_percent, 1),
            'total_space_gb': round(total / (1024**3), 2)
        }
    except Exception as e:
        raise Exception(f"Disk space check failed: {str(e)}")

def get_performance_stats():
    """Get current performance statistics."""
    return performance_monitor.get_all_stats()

def get_health_status():
    """Get current health status."""
    return health_checker.run_checks()

def log_business_event(event_type: str, **kwargs):
    """Log business events with structured data."""
    logger.info(
        "Business event",
        event_type=event_type,
        correlation_id=CorrelationIDManager.get_correlation_id(),
        **kwargs
    )

def log_security_event(event_type: str, **kwargs):
    """Log security events with structured data."""
    logger.warning(
        "Security event",
        event_type=event_type,
        correlation_id=CorrelationIDManager.get_correlation_id(),
        **kwargs
    )

def log_error(error: Exception, **context):
    """Log errors with structured data."""
    logger.error(
        "Application error",
        error_type=type(error).__name__,
        error_message=str(error),
        correlation_id=CorrelationIDManager.get_correlation_id(),
        **context
    )
