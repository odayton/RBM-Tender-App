# app/utils/db_utils/cache/cache_manager.py

from typing import Dict, List, Any, Optional, Set, Union
import logging
from datetime import datetime, timedelta
import json
from redis.exceptions import RedisError
from app.core.core_database import DatabaseManager, DatabaseError
from .query_cache import QueryCache

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages cache configuration, monitoring, and maintenance.
    Provides comprehensive cache management features including:
    - Cache rules configuration
    - Performance monitoring
    - Cache optimization
    - Memory management
    - Statistics and reporting
    """

    def __init__(self, query_cache: QueryCache):
        self.query_cache = query_cache
        self.monitored_patterns = set()
        self._initialize_cache_tables()

    def _initialize_cache_tables(self) -> None:
        """Initialize cache management tables"""
        try:
            queries = [
                # Cache rules table
                """
                CREATE TABLE IF NOT EXISTS cache_rules (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL UNIQUE,
                    ttl INTEGER NOT NULL,
                    invalidation_patterns JSONB,
                    enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Cache metrics table
                """
                CREATE TABLE IF NOT EXISTS cache_metrics (
                    id SERIAL PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    hit BOOLEAN NOT NULL,
                    response_time FLOAT NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    memory_used INTEGER,
                    key_count INTEGER
                );
                
                CREATE INDEX IF NOT EXISTS idx_cache_metrics_pattern 
                ON cache_metrics(pattern, timestamp);
                """,
                # Cache events table
                """
                CREATE TABLE IF NOT EXISTS cache_events (
                    id SERIAL PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    pattern TEXT,
                    details JSONB,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error initializing cache tables: {str(e)}")
            raise DatabaseError(f"Failed to initialize cache tables: {str(e)}")

    def configure_cache_rules(
        self,
        table_name: str,
        ttl: int,
        invalidation_patterns: Optional[List[str]] = None,
        enabled: bool = True
    ) -> None:
        """
        Configure caching rules for a table
        
        Args:
            table_name: Name of the table to configure
            ttl: Cache time-to-live in seconds
            invalidation_patterns: List of patterns that should trigger cache invalidation
            enabled: Whether caching is enabled for this table
        """
        try:
            # Validate TTL
            if ttl < 0:
                raise ValueError("TTL must be non-negative")

            query = """
                INSERT INTO cache_rules (
                    table_name, ttl, invalidation_patterns, enabled,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (table_name) DO UPDATE SET
                    ttl = EXCLUDED.ttl,
                    invalidation_patterns = EXCLUDED.invalidation_patterns,
                    enabled = EXCLUDED.enabled,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            DatabaseManager.execute_query(
                query,
                (table_name, ttl, json.dumps(invalidation_patterns or []), enabled)
            )
            
            # Update monitored patterns
            if invalidation_patterns:
                self.monitored_patterns.update(invalidation_patterns)
                
            # Log configuration event
            self._log_cache_event(
                'CONFIGURATION',
                table_name,
                {
                    'ttl': ttl,
                    'patterns': invalidation_patterns,
                    'enabled': enabled
                }
            )

        except Exception as e:
            logger.error(f"Error configuring cache rules: {str(e)}")
            raise DatabaseError(f"Failed to configure cache rules: {str(e)}")

    def monitor_cache_performance(
        self,
        time_window: int = 3600,
        pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Monitor cache performance metrics
        
        Args:
            time_window: Time window in seconds to analyze
            pattern: Optional specific pattern to monitor
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            start_time = datetime.now() - timedelta(seconds=time_window)
            
            query = """
                SELECT 
                    pattern,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN hit THEN 1 ELSE 0 END) as hits,
                    AVG(response_time) as avg_response_time,
                    MAX(response_time) as max_response_time,
                    AVG(memory_used) as avg_memory_used,
                    MAX(memory_used) as peak_memory_used,
                    AVG(key_count) as avg_key_count
                FROM cache_metrics
                WHERE timestamp >= %s
            """
            params = [start_time]
            
            if pattern:
                query += " AND pattern = %s"
                params.append(pattern)
                
            query += " GROUP BY pattern"
            
            metrics = DatabaseManager.execute_query(query, tuple(params))
            
            # Get current Redis stats
            redis_stats = self.query_cache.get_cache_stats()
            
            # Calculate performance indicators
            performance = {
                'patterns': {
                    m['pattern']: {
                        'hit_rate': (m['hits'] / m['total_requests']) * 100,
                        'avg_response_time': m['avg_response_time'],
                        'max_response_time': m['max_response_time'],
                        'memory_usage': {
                            'average': m['avg_memory_used'],
                            'peak': m['peak_memory_used']
                        },
                        'key_stats': {
                            'average': m['avg_key_count'],
                            'current': len(self.query_cache.redis.keys(m['pattern']))
                        }
                    } for m in metrics
                },
                'global_stats': {
                    **redis_stats,
                    'monitoring_window': time_window,
                    'patterns_monitored': len(metrics)
                }
            }
            
            # Log significant performance events
            for pattern_stats in performance['patterns'].values():
                if pattern_stats['hit_rate'] < 50:
                    self._log_cache_event(
                        'LOW_HIT_RATE',
                        pattern,
                        pattern_stats
                    )
                if pattern_stats['avg_response_time'] > 1.0:
                    self._log_cache_event(
                        'HIGH_RESPONSE_TIME',
                        pattern,
                        pattern_stats
                    )

            return performance

        except Exception as e:
            logger.error(f"Error monitoring cache: {str(e)}")
            raise DatabaseError(f"Failed to monitor cache: {str(e)}")

    def optimize_cache_rules(
        self,
        min_hit_rate: float = 50.0,
        max_response_time: float = 1.0,
        max_memory_percent: float = 75.0
    ) -> List[Dict[str, Any]]:
        """
        Optimize cache rules based on usage patterns
        
        Args:
            min_hit_rate: Minimum acceptable hit rate percentage
            max_response_time: Maximum acceptable response time in seconds
            max_memory_percent: Maximum memory usage percentage
            
        Returns:
            List of optimization recommendations
        """
        try:
            # Analyze recent performance
            metrics = self.monitor_cache_performance(time_window=86400)
            recommendations = []
            
            for pattern, stats in metrics['patterns'].items():
                pattern_recommendations = []
                
                # Analyze hit rate
                if stats['hit_rate'] < min_hit_rate:
                    pattern_recommendations.append({
                        'type': 'hit_rate',
                        'current': stats['hit_rate'],
                        'threshold': min_hit_rate,
                        'suggestions': [
                            'Consider reducing TTL',
                            'Review invalidation patterns',
                            'Evaluate cache necessity'
                        ]
                    })
                
                # Analyze response time
                if stats['avg_response_time'] > max_response_time:
                    pattern_recommendations.append({
                        'type': 'response_time',
                        'current': stats['avg_response_time'],
                        'threshold': max_response_time,
                        'suggestions': [
                            'Optimize underlying queries',
                            'Review serialization process',
                            'Consider data partitioning'
                        ]
                    })
                
                # Analyze memory usage
                memory_percent = (
                    stats['memory_usage']['peak'] / 
                    metrics['global_stats']['memory_used']
                ) * 100
                
                if memory_percent > max_memory_percent:
                    pattern_recommendations.append({
                        'type': 'memory_usage',
                        'current_percent': memory_percent,
                        'threshold': max_memory_percent,
                        'suggestions': [
                            'Implement data compression',
                            'Reduce cached data size',
                            'Increase cleanup frequency'
                        ]
                    })
                
                if pattern_recommendations:
                    recommendations.append({
                        'pattern': pattern,
                        'issues': pattern_recommendations,
                        'priority': len(pattern_recommendations)
                    })
            
            # Sort by priority
            recommendations.sort(key=lambda x: x['priority'], reverse=True)
            
            # Log optimization recommendations
            self._log_cache_event(
                'OPTIMIZATION',
                None,
                {'recommendations': recommendations}
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error optimizing cache rules: {str(e)}")
            raise DatabaseError(f"Failed to optimize cache rules: {str(e)}")

    def manage_memory(
        self,
        max_memory_mb: int = 1024,
        cleanup_threshold: float = 0.9
    ) -> Dict[str, Any]:
        """
        Manage cache memory usage
        
        Args:
            max_memory_mb: Maximum allowed memory usage in MB
            cleanup_threshold: Memory threshold to trigger cleanup
            
        Returns:
            Memory management statistics
        """
        try:
            stats = self.query_cache.get_cache_stats()
            current_memory_mb = int(stats['memory_used'].rstrip('B').rstrip('M'))
            
            if current_memory_mb >= (max_memory_mb * cleanup_threshold):
                # Get least used patterns
                query = """
                    SELECT pattern, COUNT(*) as access_count
                    FROM cache_metrics
                    WHERE timestamp >= NOW() - INTERVAL '1 day'
                    GROUP BY pattern
                    ORDER BY access_count ASC
                """
                least_used = DatabaseManager.execute_query(query)
                
                cleared_memory = 0
                cleared_patterns = []
                
                # Clear least used patterns until under threshold
                for pattern_data in least_used:
                    pattern = pattern_data['pattern']
                    pattern_size = self.get_pattern_size(pattern)
                    
                    self.query_cache.invalidate_pattern(pattern)
                    cleared_memory += pattern_size
                    cleared_patterns.append(pattern)
                    
                    new_memory = current_memory_mb - (cleared_memory / 1024 / 1024)
                    if new_memory < (max_memory_mb * cleanup_threshold):
                        break
                
                # Log memory management event
                self._log_cache_event(
                    'MEMORY_CLEANUP',
                    None,
                    {
                        'cleared_memory_mb': cleared_memory / 1024 / 1024,
                        'cleared_patterns': cleared_patterns
                    }
                )
                
                return {
                    'action': 'cleanup_performed',
                    'cleared_memory_mb': cleared_memory / 1024 / 1024,
                    'cleared_patterns': cleared_patterns,
                    'new_memory_mb': new_memory
                }
            
            return {
                'action': 'no_cleanup_needed',
                'current_memory_mb': current_memory_mb,
                'threshold_mb': max_memory_mb * cleanup_threshold
            }

        except Exception as e:
            logger.error(f"Error managing memory: {str(e)}")
            raise DatabaseError(f"Failed to manage memory: {str(e)}")

    def get_pattern_size(self, pattern: str) -> int:
        """Get total memory size for a cache pattern"""
        try:
            total_size = 0
            for key in self.query_cache.redis.scan_iter(pattern):
                key_size = self.query_cache.redis.memory_usage(key)
                total_size += key_size or 0
            return total_size
        except RedisError as e:
            logger.error(f"Redis error getting pattern size: {str(e)}")
            return 0

    def _log_cache_event(
        self,
        event_type: str,
        pattern: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """Log cache-related events"""
        try:
            query = """
                INSERT INTO cache_events 
                (event_type, pattern, details, timestamp)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """
            DatabaseManager.execute_query(
                query,
                (event_type, pattern, json.dumps(details))
            )
        except Exception as e:
            logger.error(f"Error logging cache event: {str(e)}")

    def get_cache_analysis(
        self, 
        time_window: int = 86400
    ) -> Dict[str, Any]:
        """
        Get comprehensive cache analysis
        
        Returns:
            Dictionary containing various cache analytics
        """
        try:
            performance = self.monitor_cache_performance(time_window)
            recommendations = self.optimize_cache_rules()
            
            # Get event statistics
            query = """
                SELECT 
                    event_type,
                    COUNT(*) as count,
                    MAX(timestamp) as last_occurrence
                FROM cache_events
                WHERE timestamp >= NOW() - INTERVAL '%s seconds'
                GROUP BY event_type
            """
            events = DatabaseManager.execute_query(query, (time_window,))
            
            return {
                'performance': performance,
                'recommendations': recommendations,
                'events': {
                    e['event_type']: {
                        'count': e['count'],
                        'last_occurrence': e['last_occurrence']
                    } for e in events
                },
                'current_rules': self.get_cache_rules(),
                'analysis_period': f"{time_window} seconds"
            }

        except Exception as e:
            logger.error(f"Error getting cache analysis: {str(e)}")
            raise DatabaseError(f"Failed to get cache analysis: {str(e)}")

    def get_cache_rules(self) -> List[Dict[str, Any]]:
        """Get all configured cache rules"""
        try:
            query = "SELECT * FROM cache_rules ORDER BY table_name"
            return DatabaseManager.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting cache rules: {str(e)}")
            raise DatabaseError(f"Failed to get cache rules: {str(e)}")