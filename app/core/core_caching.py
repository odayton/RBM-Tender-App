"""
Core Caching Module - Advanced Caching Strategies with Redis
"""

import json
import time
import hashlib
import logging
from typing import Any, Optional, Dict, List, Callable
from functools import wraps
from flask import current_app, request, g
from flask_caching import Cache
import redis
from redis.exceptions import RedisError
import structlog

logger = structlog.get_logger(__name__)

class AdvancedCache:
    """Advanced caching system with multiple strategies and Redis backend."""
    
    def __init__(self, app=None):
        self.cache = None
        self.redis_client = None
        self.cache_strategies = {}
        self._init_strategies()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize caching with Flask app."""
        # Configure Flask-Caching
        cache_config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': app.config.get('REDIS_HOST', 'localhost'),
            'CACHE_REDIS_PORT': app.config.get('REDIS_PORT', 6379),
            'CACHE_REDIS_DB': app.config.get('REDIS_DB', 0),
            'CACHE_REDIS_PASSWORD': app.config.get('REDIS_PASSWORD'),
            'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default
            'CACHE_KEY_PREFIX': 'rbm_tender_app:',
            'CACHE_SERIALIZE_METHOD': 'json'
        }
        
        self.cache = Cache(app, config=cache_config)
        
        # Initialize Redis client for advanced operations
        try:
            self.redis_client = redis.Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                db=app.config.get('REDIS_DB', 0),
                password=app.config.get('REDIS_PASSWORD'),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except RedisError as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self.redis_client = None
        
        # Register cache strategies
        self._register_strategies()
        
        logger.info("Advanced caching system initialized")
    
    def _init_strategies(self):
        """Initialize caching strategies."""
        self.cache_strategies = {
            'user_session': {
                'timeout': 3600,  # 1 hour
                'key_prefix': 'user_session:',
                'description': 'User session data'
            },
            'deal_data': {
                'timeout': 1800,  # 30 minutes
                'key_prefix': 'deal:',
                'description': 'Deal information and related data'
            },
            'quote_data': {
                'timeout': 900,   # 15 minutes
                'key_prefix': 'quote:',
                'description': 'Quote data and calculations'
            },
            'product_catalog': {
                'timeout': 7200,  # 2 hours
                'key_prefix': 'products:',
                'description': 'Product catalog and pricing'
            },
            'company_contacts': {
                'timeout': 3600,  # 1 hour
                'key_prefix': 'company:',
                'description': 'Company and contact information'
            },
            'search_results': {
                'timeout': 600,   # 10 minutes
                'key_prefix': 'search:',
                'description': 'Search results and filters'
            },
            'api_response': {
                'timeout': 300,   # 5 minutes
                'key_prefix': 'api:',
                'description': 'API response caching'
            },
            'static_data': {
                'timeout': 86400, # 24 hours
                'key_prefix': 'static:',
                'description': 'Static configuration data'
            }
        }
    
    def _register_strategies(self):
        """Register cache strategies with the app."""
        if not self.redis_client:
            return
        
        # Create strategy-specific cache instances
        for strategy_name, config in self.cache_strategies.items():
            try:
                # Store strategy config for later use
                setattr(self, f'{strategy_name}_config', config)
                logger.info(f"Registered cache strategy: {strategy_name}")
            except Exception as e:
                logger.error(f"Failed to register strategy {strategy_name}", error=str(e))
    
    def get_strategy_config(self, strategy: str) -> Dict[str, Any]:
        """Get configuration for a specific caching strategy."""
        return self.cache_strategies.get(strategy, {})
    
    def generate_cache_key(self, strategy: str, *args, **kwargs) -> str:
        """Generate a cache key for a specific strategy."""
        config = self.get_strategy_config(strategy)
        key_prefix = config.get('key_prefix', 'default:')
        
        # Create a hash of the arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:16]
        
        return f"{key_prefix}{key_hash}"
    
    def get(self, strategy: str, key: str) -> Optional[Any]:
        """Get data from cache using strategy-specific configuration."""
        try:
            if not self.redis_client:
                return None
            
            full_key = self.generate_cache_key(strategy, key)
            cached_data = self.redis_client.get(full_key)
            
            if cached_data:
                # Track cache hit
                self._track_cache_operation(strategy, 'hit', 'get')
                return json.loads(cached_data)
            else:
                # Track cache miss
                self._track_cache_operation(strategy, 'miss', 'get')
                return None
                
        except Exception as e:
            logger.error("Cache get operation failed", strategy=strategy, key=key, error=str(e))
            return None
    
    def set(self, strategy: str, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set data in cache using strategy-specific configuration."""
        try:
            if not self.redis_client:
                return False
            
            config = self.get_strategy_config(strategy)
            cache_timeout = timeout or config.get('timeout', 300)
            
            full_key = self.generate_cache_key(strategy, key)
            serialized_value = json.dumps(value, default=str)
            
            result = self.redis_client.setex(full_key, cache_timeout, serialized_value)
            
            if result:
                logger.debug("Cache set successful", strategy=strategy, key=key, timeout=cache_timeout)
                return True
            else:
                logger.warning("Cache set failed", strategy=strategy, key=key)
                return False
                
        except Exception as e:
            logger.error("Cache set operation failed", strategy=strategy, key=key, error=str(e))
            return False
    
    def delete(self, strategy: str, key: str) -> bool:
        """Delete data from cache."""
        try:
            if not self.redis_client:
                return False
            
            full_key = self.generate_cache_key(strategy, key)
            result = self.redis_client.delete(full_key)
            
            logger.debug("Cache delete", strategy=strategy, key=key, deleted=bool(result))
            return bool(result)
            
        except Exception as e:
            logger.error("Cache delete operation failed", strategy=strategy, key=key, error=str(e))
            return False
    
    def delete_pattern(self, strategy: str, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            if not self.redis_client:
                return 0
            
            config = self.get_strategy_config(strategy)
            key_prefix = config.get('key_prefix', 'default:')
            full_pattern = f"{key_prefix}{pattern}"
            
            keys = self.redis_client.keys(full_pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info("Cache pattern delete", strategy=strategy, pattern=pattern, deleted=result)
                return result
            return 0
            
        except Exception as e:
            logger.error("Cache pattern delete failed", strategy=strategy, pattern=pattern, error=str(e))
            return 0
    
    def invalidate_strategy(self, strategy: str) -> int:
        """Invalidate all cache entries for a strategy."""
        config = self.get_strategy_config(strategy)
        key_prefix = config.get('key_prefix', 'default:')
        return self.delete_pattern(strategy, '*')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if not self.redis_client:
                return {'error': 'Redis not available'}
            
            info = self.redis_client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    def _track_cache_operation(self, strategy: str, operation: str, cache_type: str):
        """Track cache operations for metrics."""
        try:
            from app.core.core_metrics import metrics
            if operation == 'hit':
                metrics.cache_hits_total.labels(
                    cache_type=strategy,
                    operation=cache_type
                ).inc()
            else:
                metrics.cache_misses_total.labels(
                    cache_type=strategy,
                    operation=cache_type
                ).inc()
        except Exception:
            # Metrics might not be available yet
            pass

# Global cache instance
advanced_cache = AdvancedCache()

# Decorator functions for easy caching
def cache_strategy(strategy: str, timeout: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator to cache function results using a specific strategy."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = advanced_cache.get(strategy, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            advanced_cache.set(strategy, cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def cache_invalidate(strategy: str, key_func: Optional[Callable] = None):
    """Decorator to invalidate cache after function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
                advanced_cache.delete(strategy, cache_key)
            else:
                # Invalidate all keys for this strategy
                advanced_cache.invalidate_strategy(strategy)
            
            return result
        return wrapper
    return decorator

# Specific caching decorators for common use cases
def cache_deal_data(timeout: int = 1800):
    """Cache deal-related data."""
    return cache_strategy('deal_data', timeout)

def cache_quote_data(timeout: int = 900):
    """Cache quote-related data."""
    return cache_strategy('quote_data', timeout)

def cache_product_data(timeout: int = 7200):
    """Cache product catalog data."""
    return cache_strategy('product_catalog', timeout)

def cache_search_results(timeout: int = 600):
    """Cache search results."""
    return cache_strategy('search_results', timeout)

def cache_api_response(timeout: int = 300):
    """Cache API responses."""
    return cache_strategy('api_response', timeout)

# Cache invalidation decorators
def invalidate_deal_cache():
    """Invalidate deal-related cache."""
    return cache_invalidate('deal_data')

def invalidate_quote_cache():
    """Invalidate quote-related cache."""
    return cache_invalidate('quote_data')

def invalidate_product_cache():
    """Invalidate product cache."""
    return cache_invalidate('product_catalog')

# Utility functions
def warm_cache():
    """Warm up commonly used cache entries."""
    try:
        # This would be called during application startup
        # to pre-populate frequently accessed data
        logger.info("Starting cache warm-up process")
        
        # Add specific warm-up logic here based on your application needs
        # For example:
        # - Load frequently accessed products
        # - Pre-calculate common search results
        # - Cache static configuration data
        
        logger.info("Cache warm-up completed")
        
    except Exception as e:
        logger.error("Cache warm-up failed", error=str(e))

def clear_all_cache():
    """Clear all application cache."""
    try:
        if advanced_cache.redis_client:
            advanced_cache.redis_client.flushdb()
            logger.info("All cache cleared")
            return True
        return False
    except Exception as e:
        logger.error("Failed to clear cache", error=str(e))
        return False

