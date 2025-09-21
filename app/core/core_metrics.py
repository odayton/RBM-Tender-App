"""
Core Metrics Module - Prometheus Integration for Application Performance Monitoring
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from flask import request, g, current_app
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, REGISTRY
)
from prometheus_client.exposition import make_wsgi_app
import structlog

logger = structlog.get_logger(__name__)

class PrometheusMetrics:
    """Prometheus metrics collector for the RBM Tender App."""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize all Prometheus metrics."""
        
        # HTTP Request Metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float('inf')),
            registry=self.registry
        )
        
        # Business Logic Metrics
        self.deals_created_total = Counter(
            'deals_created_total',
            'Total number of deals created',
            ['deal_type', 'stage'],
            registry=self.registry
        )
        
        self.quotes_generated_total = Counter(
            'quotes_generated_total',
            'Total number of quotes generated',
            ['quote_type', 'status'],
            registry=self.registry
        )
        
        self.users_active = Gauge(
            'users_active',
            'Number of currently active users',
            registry=self.registry
        )
        
        self.database_connections = Gauge(
            'database_connections_active',
            'Number of active database connections',
            registry=self.registry
        )
        
        # Performance Metrics
        self.database_query_duration_seconds = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type', 'table'],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf')),
            registry=self.registry
        )
        
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total number of cache hits',
            ['cache_type', 'operation'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total number of cache misses',
            ['cache_type', 'operation'],
            registry=self.registry
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['error_type', 'severity', 'component'],
            registry=self.registry
        )
        
        # System Metrics
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Current memory usage in bytes',
            ['component'],
            registry=self.registry
        )
        
        self.disk_usage_bytes = Gauge(
            'disk_usage_bytes',
            'Current disk usage in bytes',
            ['path'],
            registry=self.registry
        )
        
        # Custom Business Metrics
        self.deal_value_total = Counter(
            'deal_value_total',
            'Total value of all deals',
            ['deal_type', 'stage'],
            registry=self.registry
        )
        
        self.quote_value_total = Counter(
            'quote_value_total',
            'Total value of all quotes',
            ['quote_type', 'status'],
            registry=self.registry
        )
        
        # Authentication Metrics
        self.login_attempts_total = Counter(
            'login_attempts_total',
            'Total number of login attempts',
            ['result', 'user_type'],
            registry=self.registry
        )
        
        self.two_factor_attempts_total = Counter(
            'two_factor_attempts_total',
            'Total number of 2FA attempts',
            ['result'],
            registry=self.registry
        )
        
        # File Upload Metrics
        self.file_uploads_total = Counter(
            'file_uploads_total',
            'Total number of file uploads',
            ['file_type', 'status'],
            registry=self.registry
        )
        
        self.file_upload_size_bytes = Histogram(
            'file_upload_size_bytes',
            'Size of uploaded files in bytes',
            ['file_type'],
            buckets=(1024, 10240, 102400, 1048576, 10485760, 104857600, 1073741824, float('inf')),
            registry=self.registry
        )

# Global metrics instance
metrics = PrometheusMetrics()

def track_http_request(func):
    """Decorator to track HTTP request metrics."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = func(*args, **kwargs)
            
            # Extract endpoint from request
            endpoint = request.endpoint or 'unknown'
            method = request.method
            status_code = getattr(response, 'status_code', 200)
            
            # Record metrics
            metrics.http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            duration = time.time() - start_time
            metrics.http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            metrics.errors_total.labels(
                error_type=type(e).__name__,
                severity='error',
                component='http_request'
            ).inc()
            raise
    
    return wrapper

def track_database_query(query_type: str, table: str = 'unknown'):
    """Decorator to track database query performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                metrics.database_query_duration_seconds.labels(
                    query_type=query_type,
                    table=table
                ).observe(duration)
                
                return result
                
            except Exception as e:
                metrics.errors_total.labels(
                    error_type=type(e).__name__,
                    severity='error',
                    component='database'
                ).inc()
                raise
        
        return wrapper
    return decorator

def track_business_operation(operation_type: str, **labels):
    """Decorator to track business operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record operation success
                metrics.http_requests_total.labels(
                    method='business_operation',
                    endpoint=operation_type,
                    status_code='200'
                ).inc()
                
                return result
                
            except Exception as e:
                # Record operation failure
                metrics.errors_total.labels(
                    error_type=type(e).__name__,
                    severity='error',
                    component=operation_type
                ).inc()
                raise
        
        return wrapper
    return decorator

def track_cache_operation(cache_type: str, operation: str):
    """Track cache hit/miss operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                if result is not None:
                    metrics.cache_hits_total.labels(
                        cache_type=cache_type,
                        operation=operation
                    ).inc()
                else:
                    metrics.cache_misses_total.labels(
                        cache_type=cache_type,
                        operation=operation
                    ).inc()
                
                return result
                
            except Exception as e:
                metrics.errors_total.labels(
                    error_type=type(e).__name__,
                    severity='error',
                    component='cache'
                ).inc()
                raise
        
        return wrapper
    return decorator

class MetricsCollector:
    """Collects and updates system metrics."""
    
    @staticmethod
    def update_system_metrics():
        """Update system-level metrics."""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics.memory_usage_bytes.labels(component='app').set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            metrics.disk_usage_bytes.labels(path='/').set(disk.used)
            
        except ImportError:
            logger.warning("psutil not available - system metrics disabled")
        except Exception as e:
            logger.error("Failed to update system metrics", error=str(e))

def init_metrics(app):
    """Initialize metrics for the Flask app."""
    
    # Add metrics endpoint
    @app.route('/metrics')
    def metrics_endpoint():
        """Prometheus metrics endpoint."""
        # Update system metrics
        MetricsCollector.update_system_metrics()
        
        # Generate metrics
        data = generate_latest(metrics.registry)
        return data, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    
    # Add health check with metrics
    @app.route('/health/metrics')
    def health_metrics():
        """Health check endpoint with basic metrics."""
        try:
            # Get basic metrics
            data = generate_latest(metrics.registry)
            
            return {
                'status': 'healthy',
                'metrics_available': True,
                'timestamp': time.time()
            }, 200
            
        except Exception as e:
            logger.error("Metrics health check failed", error=str(e))
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }, 500
    
    logger.info("Prometheus metrics initialized", 
                metrics_endpoint='/metrics',
                health_endpoint='/health/metrics')

# Utility functions for manual metric recording
def record_deal_created(deal_type: str, stage: str, value: float = 0):
    """Record a deal creation event."""
    metrics.deals_created_total.labels(
        deal_type=deal_type,
        stage=stage
    ).inc()
    
    if value > 0:
        metrics.deal_value_total.labels(
            deal_type=deal_type,
            stage=stage
        ).inc(value)

def record_quote_generated(quote_type: str, status: str, value: float = 0):
    """Record a quote generation event."""
    metrics.quotes_generated_total.labels(
        quote_type=quote_type,
        status=status
    ).inc()
    
    if value > 0:
        metrics.quote_value_total.labels(
            quote_type=quote_type,
            status=status
        ).inc(value)

def record_login_attempt(result: str, user_type: str = 'standard'):
    """Record a login attempt."""
    metrics.login_attempts_total.labels(
        result=result,
        user_type=user_type
    ).inc()

def record_2fa_attempt(result: str):
    """Record a 2FA attempt."""
    metrics.two_factor_attempts_total.labels(result=result).inc()

def record_file_upload(file_type: str, status: str, size_bytes: int = 0):
    """Record a file upload event."""
    metrics.file_uploads_total.labels(
        file_type=file_type,
        status=status
    ).inc()
    
    if size_bytes > 0:
        metrics.file_upload_size_bytes.labels(
            file_type=file_type
        ).observe(size_bytes)

def record_error(error_type: str, severity: str, component: str):
    """Record an error event."""
    metrics.errors_total.labels(
        error_type=error_type,
        severity=severity,
        component=component
    ).inc()

