"""
Monitoring Routes - Health checks, metrics, and monitoring endpoints
"""

import time
from datetime import datetime, timedelta
from flask import jsonify, request, current_app
from app.features.monitoring import monitoring_bp
from app.core.core_monitoring import (
    health_checker, 
    performance_monitor, 
    get_performance_stats, 
    get_health_status,
    log_business_event,
    CorrelationIDManager
)
from app.core.core_sentry import (
    capture_business_event,
    capture_performance_metric,
    add_breadcrumb
)
from app.core.core_security import admin_required

@monitoring_bp.route('/health')
def health_check():
    """Basic health check endpoint."""
    try:
        # Run health checks
        health_status = get_health_status()
        
        # Determine HTTP status code
        status_code = 200 if health_status['overall_status'] == 'healthy' else 503
        
        # Add response time
        health_status['response_time_ms'] = round(time.time() * 1000, 2)
        
        return jsonify(health_status), status_code
    
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@monitoring_bp.route('/health/detailed')
@admin_required
def detailed_health_check():
    """Detailed health check endpoint for administrators."""
    try:
        # Run comprehensive health checks
        health_status = get_health_status()
        
        # Add additional system information
        health_status.update({
            'system_info': {
                'python_version': current_app.config.get('PYTHON_VERSION', 'Unknown'),
                'flask_version': current_app.config.get('FLASK_VERSION', 'Unknown'),
                'environment': current_app.config.get('ENV', 'development'),
                'debug_mode': current_app.debug,
                'testing_mode': current_app.config.get('TESTING', False)
            },
            'request_info': {
                'correlation_id': CorrelationIDManager.get_correlation_id(),
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
        # Log health check access
        log_business_event('health_check_detailed', 
                          correlation_id=CorrelationIDManager.get_correlation_id())
        
        return jsonify(health_status)
    
    except Exception as e:
        current_app.logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@monitoring_bp.route('/metrics')
@admin_required
def performance_metrics():
    """Performance metrics endpoint."""
    try:
        # Get performance statistics
        metrics = get_performance_stats()
        
        # Add system metrics
        metrics.update({
            'system_metrics': {
                'uptime_seconds': time.time() - current_app.config.get('START_TIME', time.time()),
                'request_count': len(performance_monitor.metrics.get('request', [])),
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
        # Log metrics access
        log_business_event('metrics_accessed', 
                          correlation_id=CorrelationIDManager.get_correlation_id())
        
        return jsonify(metrics)
    
    except Exception as e:
        current_app.logger.error(f"Metrics retrieval failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/metrics/reset')
@admin_required
def reset_metrics():
    """Reset performance metrics (admin only)."""
    try:
        # Reset performance monitor
        performance_monitor.metrics.clear()
        performance_monitor.start_times.clear()
        
        # Log metrics reset
        log_business_event('metrics_reset', 
                          correlation_id=CorrelationIDManager.get_correlation_id())
        
        return jsonify({
            'message': 'Metrics reset successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        current_app.logger.error(f"Metrics reset failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/status')
def system_status():
    """System status endpoint for load balancers."""
    try:
        # Quick status check
        status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': current_app.config.get('VERSION', '1.0.0'),
            'environment': current_app.config.get('ENV', 'development')
        }
        
        # Add basic health check
        try:
            from app.core.core_database import db
            db.session.execute('SELECT 1')
            status['database'] = 'healthy'
        except Exception:
            status['database'] = 'unhealthy'
            status['status'] = 'unhealthy'
        
        return jsonify(status), 200 if status['status'] == 'healthy' else 503
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@monitoring_bp.route('/ping')
def ping():
    """Simple ping endpoint for connectivity testing."""
    return jsonify({
        'message': 'pong',
        'timestamp': datetime.utcnow().isoformat(),
        'correlation_id': CorrelationIDManager.get_correlation_id()
    })

@monitoring_bp.route('/info')
@admin_required
def system_info():
    """System information endpoint for administrators."""
    try:
        import platform
        import psutil
        import sys
        
        info = {
            'application': {
                'name': 'RBM Tender App',
                'version': current_app.config.get('VERSION', '1.0.0'),
                'environment': current_app.config.get('ENV', 'development'),
                'debug_mode': current_app.debug,
                'testing_mode': current_app.config.get('TESTING', False)
            },
            'system': {
                'platform': platform.platform(),
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'disk_usage_percent': psutil.disk_usage('/').percent
            },
            'database': {
                'type': 'PostgreSQL',
                'url': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log system info access
        log_business_event('system_info_accessed', 
                          correlation_id=CorrelationIDManager.get_correlation_id())
        
        return jsonify(info)
    
    except Exception as e:
        current_app.logger.error(f"System info retrieval failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/logs')
@admin_required
def recent_logs():
    """Recent application logs endpoint."""
    try:
        # This would typically read from log files
        # For now, return a placeholder
        logs = {
            'message': 'Log access not yet implemented',
            'note': 'This endpoint will provide access to recent application logs',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(logs)
    
    except Exception as e:
        current_app.logger.error(f"Log retrieval failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/test-error')
@admin_required
def test_error():
    """Test error endpoint for Sentry integration testing."""
    try:
        # This will trigger an error for testing
        raise Exception("This is a test error for Sentry integration")
    
    except Exception as e:
        from app.core.core_sentry import capture_exception
        capture_exception(e, test_error=True)
        return jsonify({
            'message': 'Test error captured and sent to Sentry',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.route('/test-performance')
@admin_required
def test_performance():
    """Test performance monitoring endpoint."""
    try:
        from app.core.core_monitoring import performance_context
        
        # Simulate some work
        with performance_context('test_operation', test=True):
            time.sleep(0.1)  # Simulate 100ms operation
        
        return jsonify({
            'message': 'Performance test completed',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        current_app.logger.error(f"Performance test failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

