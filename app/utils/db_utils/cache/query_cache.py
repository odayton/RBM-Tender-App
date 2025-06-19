# app/utils/db_utils/cache/query_cache.py

from typing import Dict, List, Any, Optional, Union, Callable
import logging
import hashlib
import json
from datetime import datetime, timedelta
import redis
from functools import wraps
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class QueryCache:
    """
    Handles database query caching using Redis.
    Provides decorators and utilities for automatic query caching.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour default TTL

    def cache_query(
        self,
        ttl: Optional[int] = None,
        key_prefix: Optional[str] = None,
        invalidate_keys: Optional[List[str]] = None
    ):
        """
        Decorator for caching query results.
        
        Args:
            ttl: Cache TTL in seconds
            key_prefix: Prefix for cache key
            invalidate_keys: List of cache keys to invalidate
            
        Usage:
            @query_cache.cache_query(ttl=3600)
            def get_user_data(user_id: int):
                # Function implementation
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    func.__name__,
                    key_prefix,
                    args,
                    kwargs
                )

                # Try to get from cache
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result

                # Execute query and cache result
                result = func(*args, **kwargs)
                self._set_in_cache(cache_key, result, ttl or self.default_ttl)

                # Invalidate related keys if specified
                if invalidate_keys:
                    self.invalidate_keys(invalidate_keys)

                return result
            return wrapper
        return decorator

    def _generate_cache_key(
        self,
        func_name: str,
        prefix: Optional[str],
        args: tuple,
        kwargs: dict
    ) -> str:
        """Generate unique cache key"""
        key_parts = [
            prefix or 'query',
            func_name,
            hashlib.md5(
                json.dumps({
                    'args': args,
                    'kwargs': kwargs
                }, sort_keys=True).encode()
            ).hexdigest()
        ]
        return ':'.join(key_parts)

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieve data from cache"""
        try:
            cached_data = self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None

    def _set_in_cache(self, key: str, value: Any, ttl: int) -> None:
        """Store data in cache"""
        try:
            self.redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")

    def invalidate_keys(self, keys: List[str]) -> None:
        """Invalidate specific cache keys"""
        try:
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error invalidating cache keys: {str(e)}")

    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {str(e)}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis.info()
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'total_keys': self.redis.dbsize(),
                'memory_used': info.get('used_memory_human', '0B')
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}

    def clear_cache(self) -> None:
        """Clear entire cache"""
        try:
            self.redis.flushdb()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific cache key"""
        try:
            if not self.redis.exists(key):
                return None

            ttl = self.redis.ttl(key)
            value = self.redis.get(key)
            
            return {
                'key': key,
                'ttl': ttl,
                'size': len(value) if value else 0,
                'type': self.redis.type(key).decode()
            }
        except Exception as e:
            logger.error(f"Error getting key info: {str(e)}")
            return None