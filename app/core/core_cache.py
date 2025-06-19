# app/core/core_cache.py

from typing import Any, Optional, Dict, List, Union, Set
import time
import json
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import logging
from threading import Lock
import redis
from dataclasses import dataclass

from ..app_constants import (
    CACHE_TIMEOUT,
    MAX_CACHE_SIZE,
    CACHE_KEY_PREFIX,
    CACHE_CLEANUP_INTERVAL
)
from .core_logging import core_logger

logger = logging.getLogger(__name__)

@dataclass
class CacheItem:
    """Data structure for cached items"""
    value: Any
    expiry: float
    tags: List[str]
    last_accessed: float
    access_count: int

class CacheManager:
    """
    Unified cache management system combining Redis and in-memory caching
    with comprehensive monitoring and optimization.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._memory_cache: Dict[str, CacheItem] = {}
        self._redis = redis.from_url(redis_url) if redis_url else None
        self._lock = Lock()
        self._last_cleanup = time.time()
        
        # Cache statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'memory_items': 0,
            'redis_items': 0,
            'evictions': 0
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get item from cache (memory or Redis)
        Args:
            key: Cache key
            default: Default value if key not found
        Returns:
            Cached value or default
        """
        prefixed_key = self._prefix_key(key)
        
        # Try memory cache first
        with self._lock:
            if item := self._memory_cache.get(prefixed_key):
                if time.time() <= item.expiry:
                    item.last_accessed = time.time()
                    item.access_count += 1
                    self._stats['hits'] += 1
                    return item.value
                else:
                    del self._memory_cache[prefixed_key]

        # Try Redis if available
        if self._redis:
            try:
                if value := self._redis.get(prefixed_key):
                    self._stats['hits'] += 1
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis error getting key {key}: {str(e)}")

        self._stats['misses'] += 1
        return default

    def set(
        self,
        key: str,
        value: Any,
        timeout: int = CACHE_TIMEOUT,
        tags: Optional[List[str]] = None,
        use_redis: bool = False
    ) -> None:
        """
        Store item in cache
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
            tags: List of tags for cache invalidation
            use_redis: Whether to use Redis instead of memory cache
        """
        prefixed_key = self._prefix_key(key)
        expiry = time.time() + timeout
        
        try:
            if use_redis and self._redis:
                self._redis.setex(
                    prefixed_key,
                    timeout,
                    json.dumps(value, default=str)
                )
                self._stats['redis_items'] = self._redis.dbsize()
            else:
                with self._lock:
                    # Check cache size limit
                    if len(self._memory_cache) >= MAX_CACHE_SIZE:
                        self._evict_items()

                    self._memory_cache[prefixed_key] = CacheItem(
                        value=value,
                        expiry=expiry,
                        tags=tags or [],
                        last_accessed=time.time(),
                        access_count=0
                    )
                    self._stats['memory_items'] = len(self._memory_cache)

            # Perform cleanup if needed
            self._maybe_cleanup()

        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")

    def delete(self, key: str) -> bool:
        """
        Delete item from cache
        Args:
            key: Cache key
        Returns:
            bool: Whether key was deleted
        """
        prefixed_key = self._prefix_key(key)
        deleted = False
        
        with self._lock:
            if prefixed_key in self._memory_cache:
                del self._memory_cache[prefixed_key]
                deleted = True
                self._stats['memory_items'] = len(self._memory_cache)

        if self._redis:
            try:
                if self._redis.delete(prefixed_key):
                    deleted = True
                    self._stats['redis_items'] = self._redis.dbsize()
            except Exception as e:
                logger.error(f"Redis error deleting key {key}: {str(e)}")

        return deleted

    def invalidate_tags(self, tags: List[str]) -> int:
        """
        Invalidate all cache entries with specified tags
        Args:
            tags: List of tags to invalidate
        Returns:
            int: Number of entries invalidated
        """
        count = 0
        
        # Memory cache invalidation
        with self._lock:
            keys_to_delete = [
                key for key, item in self._memory_cache.items()
                if any(tag in item.tags for tag in tags)
            ]
            
            for key in keys_to_delete:
                del self._memory_cache[key]
                count += 1
            
            self._stats['memory_items'] = len(self._memory_cache)

        # Redis invalidation if available
        if self._redis:
            try:
                for tag in tags:
                    pattern = f"{CACHE_KEY_PREFIX}*{tag}*"
                    keys = self._redis.keys(pattern)
                    if keys:
                        count += self._redis.delete(*keys)
                self._stats['redis_items'] = self._redis.dbsize()
            except Exception as e:
                logger.error(f"Redis error invalidating tags: {str(e)}")

        return count

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._memory_cache.clear()
            self._stats['memory_items'] = 0

        if self._redis:
            try:
                self._redis.flushdb()
                self._stats['redis_items'] = 0
            except Exception as e:
                logger.error(f"Redis error clearing cache: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        Returns:
            Dict containing cache statistics
        """
        with self._lock:
            stats = self._stats.copy()
            
            if self._redis:
                try:
                    redis_info = self._redis.info()
                    stats.update({
                        'redis_memory_used': redis_info.get('used_memory_human'),
                        'redis_evicted_keys': redis_info.get('evicted_keys', 0),
                        'redis_connected_clients': redis_info.get('connected_clients', 0)
                    })
                except Exception as e:
                    logger.error(f"Redis error getting stats: {str(e)}")

            return stats

    def _prefix_key(self, key: str) -> str:
        """Add prefix to cache key"""
        return f"{CACHE_KEY_PREFIX}{key}"

    def _evict_items(self, count: int = 10) -> None:
        """
        Evict least recently used items from memory cache
        Args:
            count: Number of items to evict
        """
        if not self._memory_cache:
            return

        sorted_items = sorted(
            self._memory_cache.items(),
            key=lambda x: (x[1].last_accessed, -x[1].access_count)
        )

        for key, _ in sorted_items[:count]:
            del self._memory_cache[key]
            self._stats['evictions'] += 1

    def _maybe_cleanup(self) -> None:
        """Perform periodic cache cleanup"""
        current_time = time.time()
        if current_time - self._last_cleanup >= CACHE_CLEANUP_INTERVAL:
            self.cleanup()
            self._last_cleanup = current_time

    def cleanup(self) -> int:
        """
        Remove expired entries
        Returns:
            int: Number of entries removed
        """
        count = 0
        current_time = time.time()
        
        with self._lock:
            keys_to_delete = [
                key for key, item in self._memory_cache.items()
                if current_time > item.expiry
            ]
            
            for key in keys_to_delete:
                del self._memory_cache[key]
                count += 1
            
            self._stats['memory_items'] = len(self._memory_cache)

        return count

    def memoize(self, timeout: int = CACHE_TIMEOUT, tags: Optional[List[str]] = None):
        """
        Decorator for caching function results
        Args:
            timeout: Cache timeout in seconds
            tags: List of tags for cache invalidation
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                
                cache_key = hashlib.md5(
                    ":".join(key_parts).encode()
                ).hexdigest()
                
                # Try to get from cache
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # Compute and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, timeout, tags)
                return result
            return wrapper
        return decorator

# Create global cache manager instance
cache_manager = CacheManager()

# Convenience decorators and functions
def cached(timeout: int = CACHE_TIMEOUT, tags: Optional[List[str]] = None):
    """Convenience decorator for caching"""
    return cache_manager.memoize(timeout, tags)

def invalidate_tags(tags: List[str]) -> int:
    """Convenience function for tag invalidation"""
    return cache_manager.invalidate_tags(tags)