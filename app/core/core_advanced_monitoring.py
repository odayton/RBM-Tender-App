"""
Core Advanced Monitoring Module - Real-time Dashboards and Performance Tracking
"""

import time
import json
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from flask import Blueprint, render_template, jsonify, request, current_app
from sqlalchemy import text
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    process_count: int
    thread_count: int

@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    timestamp: datetime
    active_connections: int
    max_connections: int
    connection_utilization: float
    query_count: int
    slow_query_count: int
    avg_query_time_ms: float
    cache_hit_ratio: float
    database_size_mb: float
    table_count: int
    index_count: int

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: datetime
    requests_per_minute: int
    response_time_avg_ms: float
    response_time_p95_ms: float
    error_rate_percent: float
    active_users: int
    deals_created_today: int
    quotes_generated_today: int
    cache_hit_rate: float
    feature_flags_active: int
    circuit_breakers_open: int

class MetricsCollector:
    """Collects and aggregates various system metrics."""
    
    def __init__(self, db):
        self.db = db
        self.metrics_history = {
            'system': [],
            'database': [],
            'application': []
        }
        self.max_history = 1000  # Keep last 1000 data points
        self.collection_interval = 30  # seconds
        self.is_collecting = False
        self.collection_thread = None
        
        # Initialize baseline metrics
        self._initialize_baseline()
    
    def _initialize_baseline(self):
        """Initialize baseline metrics for comparison."""
        self.baseline_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_usage_percent': 0.0,
            'network_sent_mb': 0.0,
            'network_recv_mb': 0.0
        }
        
        # Get initial network stats
        net_io = psutil.net_io_counters()
        if net_io:
            self.baseline_metrics['network_sent_mb'] = net_io.bytes_sent / (1024 * 1024)
            self.baseline_metrics['network_recv_mb'] = net_io.bytes_recv / (1024 * 1024)
    
    def start_collection(self):
        """Start continuous metrics collection."""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop continuous metrics collection."""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self):
        """Main collection loop running in background thread."""
        from flask import current_app
        app = None
        
        # Get the Flask app instance
        try:
            from app import create_app
            from app.core.core_config import ProductionConfig
            app = create_app(ProductionConfig)
        except Exception as e:
            logger.error("Failed to create app instance for monitoring", error=str(e))
            return
        
        while self.is_collecting:
            try:
                with app.app_context():
                    # Collect all metrics
                    system_metrics = self._collect_system_metrics()
                    database_metrics = self._collect_database_metrics()
                    application_metrics = self._collect_application_metrics()
                    
                    # Store metrics
                    self._store_metrics('system', system_metrics)
                    self._store_metrics('database', database_metrics)
                    self._store_metrics('application', application_metrics)
                
                # Wait for next collection
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error("Error in metrics collection loop", error=str(e))
                time.sleep(5)  # Wait before retrying
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_sent_mb = (net_io.bytes_sent - self.baseline_metrics['network_sent_mb']) / (1024 * 1024)
            network_recv_mb = (net_io.bytes_recv - self.baseline_metrics['network_recv_mb']) / (1024 * 1024)
            
            # Process information
            process_count = len(psutil.pids())
            thread_count = psutil.Process().num_threads()
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / (1024**3),
                memory_total_gb=memory.total / (1024**3),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024**3),
                disk_total_gb=disk.total / (1024**3),
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                load_average=load_avg,
                process_count=process_count,
                thread_count=thread_count
            )
            
        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                disk_total_gb=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                load_average=[0.0, 0.0, 0.0],
                process_count=0,
                thread_count=0
            )
    
    def _collect_database_metrics(self) -> DatabaseMetrics:
        """Collect database performance metrics."""
        try:
            # Use a shorter connection timeout to prevent connection pool exhaustion
            with self.db.engine.connect() as conn:
                # Connection stats
                conn_stats = conn.execute(text("""
                    SELECT 
                        count(*) as active_connections,
                        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """)).fetchone()
                
                # Query performance stats - check if pg_stat_statements extension exists
                query_stats = None
                try:
                    # First check if the extension is installed
                    extension_check = conn.execute(text("""
                        SELECT EXISTS(
                            SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                        )
                    """)).fetchone()
                    
                    if extension_check and extension_check[0]:
                        query_stats = conn.execute(text("""
                            SELECT 
                                count(*) as query_count,
                                count(*) FILTER (WHERE mean_exec_time > 1000) as slow_query_count,
                                avg(mean_exec_time) as avg_query_time_ms
                            FROM pg_stat_statements
                        """)).fetchone()
                    else:
                        # Extension not installed, use alternative query
                        query_stats = conn.execute(text("""
                            SELECT 
                                count(*) as query_count,
                                0 as slow_query_count,
                                0.0 as avg_query_time_ms
                            FROM pg_stat_activity 
                            WHERE state = 'active'
                        """)).fetchone()
                except Exception as ext_error:
                    # Fallback if pg_stat_statements query fails
                    logger.debug("pg_stat_statements not available, using fallback", error=str(ext_error))
                    query_stats = conn.execute(text("""
                        SELECT 
                            count(*) as query_count,
                            0 as slow_query_count,
                            0.0 as avg_query_time_ms
                        FROM pg_stat_activity 
                        WHERE state = 'active'
                    """)).fetchone()
                
                # Cache hit ratio
                cache_stats = conn.execute(text("""
                    SELECT 
                        round(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2) as cache_hit_ratio
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """)).fetchone()
                
                # Database size
                size_stats = conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                           pg_database_size(current_database()) / (1024*1024) as size_mb
                """)).fetchone()
                
                # Table and index count
                table_stats = conn.execute(text("""
                    SELECT 
                        count(*) as table_count,
                        (SELECT count(*) FROM pg_indexes WHERE schemaname = 'public') as index_count
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)).fetchone()
                
                active_connections = conn_stats[0] if conn_stats else 0
                max_connections = conn_stats[1] if conn_stats else 100
                connection_utilization = (active_connections / max_connections * 100) if max_connections > 0 else 0
                
                return DatabaseMetrics(
                    timestamp=datetime.utcnow(),
                    active_connections=active_connections,
                    max_connections=max_connections,
                    connection_utilization=connection_utilization,
                    query_count=query_stats[0] if query_stats else 0,
                    slow_query_count=query_stats[1] if query_stats else 0,
                    avg_query_time_ms=query_stats[2] if query_stats else 0.0,
                    cache_hit_ratio=cache_stats[0] if cache_stats else 0.0,
                    database_size_mb=size_stats[1] if size_stats else 0.0,
                    table_count=table_stats[0] if table_stats else 0,
                    index_count=table_stats[1] if table_stats else 0
                )
                
        except Exception as e:
            # Don't spam logs with connection errors or missing extension errors
            error_str = str(e).lower()
            if "too many clients" not in error_str and "pg_stat_statements" not in error_str:
                logger.error("Failed to collect database metrics", error=str(e))
            elif "pg_stat_statements" in error_str:
                logger.debug("pg_stat_statements extension not available", error=str(e))
            return DatabaseMetrics(
                timestamp=datetime.utcnow(),
                active_connections=0,
                max_connections=0,
                connection_utilization=0.0,
                query_count=0,
                slow_query_count=0,
                avg_query_time_ms=0.0,
                cache_hit_ratio=0.0,
                database_size_mb=0.0,
                table_count=0,
                index_count=0
            )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics."""
        try:
            # Get metrics from Prometheus if available
            from app.core.core_metrics import metrics
            
            # Calculate rates from counters
            requests_per_minute = 0
            response_time_avg_ms = 0.0
            response_time_p95_ms = 0.0
            error_rate_percent = 0.0
            
            # Get business metrics
            deals_created_today = 0
            quotes_generated_today = 0
            
            # Get cache hit rate
            cache_hit_rate = 0.0
            try:
                from app.core.core_caching import advanced_cache
                cache_stats = advanced_cache.get_stats()
                cache_hit_rate = cache_stats.get('hit_rate', 0.0)
            except:
                pass
            
            # Get feature flags count
            feature_flags_active = 0
            try:
                from app.core.core_feature_flags import feature_flags
                feature_flags_active = len(feature_flags.get_enabled_flags())
            except:
                pass
            
            # Get circuit breaker status
            circuit_breakers_open = 0
            try:
                from app.core.core_circuit_breaker import get_circuit_breaker_stats
                breaker_stats = get_circuit_breaker_stats()
                circuit_breakers_open = sum(
                    1 for stats in breaker_stats.values() 
                    if stats['current_state'] == 'open'
                )
            except:
                pass
            
            return ApplicationMetrics(
                timestamp=datetime.utcnow(),
                requests_per_minute=requests_per_minute,
                response_time_avg_ms=response_time_avg_ms,
                response_time_p95_ms=response_time_p95_ms,
                error_rate_percent=error_rate_percent,
                active_users=0,  # Would need session tracking
                deals_created_today=deals_created_today,
                quotes_generated_today=quotes_generated_today,
                cache_hit_rate=cache_hit_rate,
                feature_flags_active=feature_flags_active,
                circuit_breakers_open=circuit_breakers_open
            )
            
        except Exception as e:
            logger.error("Failed to collect application metrics", error=str(e))
            return ApplicationMetrics(
                timestamp=datetime.utcnow(),
                requests_per_minute=0,
                response_time_avg_ms=0.0,
                response_time_p95_ms=0.0,
                error_rate_percent=0.0,
                active_users=0,
                deals_created_today=0,
                quotes_generated_today=0,
                cache_hit_rate=0.0,
                feature_flags_active=0,
                circuit_breakers_open=0
            )
    
    def _store_metrics(self, metric_type: str, metrics: Any):
        """Store metrics in history with size limit."""
        self.metrics_history[metric_type].append(asdict(metrics))
        
        # Keep only the last max_history entries
        if len(self.metrics_history[metric_type]) > self.max_history:
            self.metrics_history[metric_type] = self.metrics_history[metric_type][-self.max_history:]
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the latest metrics for all types."""
        return {
            'system': self.metrics_history['system'][-1] if self.metrics_history['system'] else None,
            'database': self.metrics_history['database'][-1] if self.metrics_history['database'] else None,
            'application': self.metrics_history['application'][-1] if self.metrics_history['application'] else None
        }
    
    def get_metrics_history(self, metric_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for a specific type and time range."""
        if metric_type not in self.metrics_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metric for metric in self.metrics_history[metric_type]
            if datetime.fromisoformat(metric['timestamp']) > cutoff_time
        ]

# Create advanced monitoring blueprint with unique name
monitoring_bp = Blueprint('advanced_monitoring', __name__, url_prefix='/monitoring')

@monitoring_bp.route('/dashboard')
def monitoring_dashboard():
    """Main monitoring dashboard."""
    return render_template('monitoring/dashboard.html')

@monitoring_bp.route('/api/metrics/latest')
def get_latest_metrics():
    """Get latest metrics as JSON."""
    try:
        from app.core.core_advanced_monitoring import metrics_collector
        metrics = metrics_collector.get_latest_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error("Failed to get latest metrics", error=str(e))
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/metrics/history/<metric_type>')
def get_metrics_history(metric_type: str):
    """Get metrics history for a specific type."""
    try:
        hours = request.args.get('hours', 24, type=int)
        from app.core.core_advanced_monitoring import metrics_collector
        history = metrics_collector.get_metrics_history(metric_type, hours)
        return jsonify(history)
    except Exception as e:
        logger.error("Failed to get metrics history", error=str(e))
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/health')
def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # System health
        try:
            from app.core.core_advanced_monitoring import metrics_collector
            latest_metrics = metrics_collector.get_latest_metrics()
            
            if latest_metrics['system']:
                system = latest_metrics['system']
                health_status['checks']['system'] = {
                    'status': 'healthy' if system['cpu_percent'] < 80 and system['memory_percent'] < 90 else 'warning',
                    'cpu_percent': system['cpu_percent'],
                    'memory_percent': system['memory_percent'],
                    'disk_usage_percent': system['disk_usage_percent']
                }
            else:
                health_status['checks']['system'] = {'status': 'unknown'}
        except Exception as e:
            health_status['checks']['system'] = {'status': 'error', 'error': str(e)}
        
        # Database health
        try:
            from app.core.core_advanced_monitoring import metrics_collector
            latest_metrics = metrics_collector.get_latest_metrics()
            
            if latest_metrics['database']:
                db = latest_metrics['database']
                health_status['checks']['database'] = {
                    'status': 'healthy' if db['connection_utilization'] < 80 else 'warning',
                    'active_connections': db['active_connections'],
                    'connection_utilization': db['connection_utilization'],
                    'cache_hit_ratio': db['cache_hit_ratio']
                }
            else:
                health_status['checks']['database'] = {'status': 'unknown'}
        except Exception as e:
            health_status['checks']['database'] = {'status': 'error', 'error': str(e)}
        
        # Application health
        try:
            from app.core.core_advanced_monitoring import metrics_collector
            latest_metrics = metrics_collector.get_latest_metrics()
            
            if latest_metrics['application']:
                app = latest_metrics['application']
                health_status['checks']['application'] = {
                    'status': 'healthy' if app['error_rate_percent'] < 5 else 'warning',
                    'error_rate_percent': app['error_rate_percent'],
                    'cache_hit_rate': app['cache_hit_rate'],
                    'circuit_breakers_open': app['circuit_breakers_open']
                }
            else:
                health_status['checks']['application'] = {'status': 'unknown'}
        except Exception as e:
            health_status['checks']['application'] = {'status': 'error', 'error': str(e)}
        
        # Determine overall status
        check_statuses = [check['status'] for check in health_status['checks'].values()]
        if 'error' in check_statuses:
            health_status['overall_status'] = 'unhealthy'
        elif 'warning' in check_statuses:
            health_status['overall_status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'error',
            'error': str(e)
        }), 500

# Global metrics collector
metrics_collector = None

def init_advanced_monitoring(app, db):
    """Initialize advanced monitoring system."""
    global metrics_collector
    
    # Check if advanced monitoring is disabled
    if not app.config.get('ENABLE_ADVANCED_MONITORING', True):
        logger.info("Advanced monitoring system disabled via configuration")
        return None
    
    # Create metrics collector
    metrics_collector = MetricsCollector(db)
    
    # Note: Blueprint registration is handled in main app initialization
    # to avoid duplicate registration errors
    
    # Start metrics collection
    metrics_collector.start_collection()
    
    logger.info("Advanced monitoring system initialized",
                dashboard_url='/monitoring/dashboard',
                api_url='/monitoring/api/metrics/latest')
    
    return metrics_collector

def get_metrics_collector():
    """Get the global metrics collector."""
    return metrics_collector

