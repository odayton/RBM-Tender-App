from typing import Any, Optional, Dict, List
import time
import json
from functools import wraps
import hashlib
from threading import Lock
import redis
from dataclasses import dataclass, field
from flask import Flask
from .core_logging import logger # Use central app logger

@dataclass
class CacheItem:
    """Data structure for in-memory cached items."""
    value: Any
    expiry: float
    tags: List[str] = field(default_factory=list)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0

class CacheManager:
    """
    A thread-safe, unified cache management system for in-memory and Redis caching.
    Follows the Flask Extension pattern.
    """
    def __init__(self):
        self._memory_cache: Dict[str, CacheItem] = {}
        self._redis: Optional[redis.Redis] = None
        self._lock = Lock()
        self._last_cleanup = 0.0
        self.app: Optional[Flask] = None
        self._stats = {
            'hits': 0, 'misses': 0, 'memory_items': 0,
            'redis_items': 0, 'evictions': 0
        }

    def init_app(self, app: Flask):
        """Initialize the CacheManager with the Flask app config."""
        self.app = app
        redis_url = app.config.get('REDIS_URL')
        if redis_url:
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping() # Check connection
                logger.info("CacheManager connected to Redis.")
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Could not connect to Redis at {redis_url}. Redis caching will be disabled. Error: {e}", exc_info=True)
                self._redis = None
        else:
            logger.info("No REDIS_URL configured. CacheManager will use in-memory cache only.")
        self._last_cleanup = time.time()

    def get(self, key: str, default: Any = None) -> Any:
        """Get an item from the cache, trying memory first, then Redis."""
        prefixed_key = self._prefix_key(key)
        
        # Try memory cache first
        with self._lock:
            item = self._memory_cache.get(prefixed_key)
            if item:
                if time.time() <= item.expiry:
                    item.last_accessed = time.time()
                    item.access_count += 1
                    self._stats['hits'] += 1
                    return item.value
                else:
                    # Expired, delete from memory
                    del self._memory_cache[prefixed_key]
                    self._stats['evictions'] += 1
        
        # Try Redis if available
        if self._redis:
            try:
                value_str = self._redis.get(prefixed_key)
                if value_str:
                    self._stats['hits'] += 1
                    return json.loads(value_str)
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis error getting key '{key}': {e}", exc_info=True)

        self._stats['misses'] += 1
        return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None, use_redis: bool = False, tags: Optional[List[str]] = None):
        """Store an item in the cache."""
        prefixed_key = self._prefix_key(key)
        
        # Get configuration from app context
        effective_timeout = timeout or self.app.config.get('CACHE_TIMEOUT', 3600)
        expiry = time.time() + effective_timeout

        try:
            if use_redis and self._redis:
                self._redis.setex(prefixed_key, effective_timeout, json.dumps(value, default=str))
            else:
                with self._lock:
                    max_size = self.app.config.get('MAX_CACHE_SIZE', 500)
                    if len(self._memory_cache) >= max_size and prefixed_key not in self._memory_cache:
                        self._evict_items()
                    
                    self._memory_cache[prefixed_key] = CacheItem(
                        value=value, expiry=expiry, tags=tags or []
                    )
            self._maybe_cleanup()
        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}", exc_info=True)

    def delete(self, key: str) -> bool:
        """Delete an item from all cache layers."""
        prefixed_key = self._prefix_key(key)
        deleted = False
        with self._lock:
            if prefixed_key in self._memory_cache:
                del self._memory_cache[prefixed_key]
                deleted = True
        if self._redis:
            try:
                if self._redis.delete(prefixed_key):
                    deleted = True
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis error deleting key '{key}': {e}", exc_info=True)
        return deleted

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._memory_cache.clear()
        if self._redis:
            try:
                self._redis.flushdb()
                logger.warning("Cleared all keys from Redis cache.")
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis error clearing cache: {e}", exc_info=True)

    def memoize(self, timeout: Optional[int] = None):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate a key based on function and arguments
                key_parts = [func.__name__] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
                key = hashlib.md5(':'.join(key_parts).encode()).hexdigest()
                
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                self.set(key, result, timeout=timeout)
                return result
            return wrapper
        return decorator

    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats['memory_items'] = len(self._memory_cache)
            if self._redis:
                try:
                    stats['redis_items'] = self._redis.dbsize()
                except redis.exceptions.RedisError:
                    stats['redis_items'] = 'N/A'
            return stats

    def _prefix_key(self, key: str) -> str:
        prefix = self.app.config.get('CACHE_KEY_PREFIX', 'rbm:') if self.app else 'rbm:'
        return f"{prefix}{key}"

    def _evict_items(self, count: int = 10):
        """Evict least recently used items from memory cache."""
        if not self._memory_cache:
            return
        # Sort by last accessed time (oldest first), then by access count (lowest first)
        sorted_keys = sorted(
            self._memory_cache, 
            key=lambda k: (self._memory_cache[k].last_accessed, self._memory_cache[k].access_count)
        )
        for key in sorted_keys[:count]:
            if key in self._memory_cache:
                del self._memory_cache[key]
                self._stats['evictions'] += 1
        logger.warning(f"Evicted {count} items from in-memory cache.")

    def _maybe_cleanup(self):
        """Perform periodic cleanup of expired items."""
        cleanup_interval = self.app.config.get('CACHE_CLEANUP_INTERVAL', 60) if self.app else 60
        if time.time() - self._last_cleanup >= cleanup_interval:
            expired_count = self.cleanup()
            self._last_cleanup = time.time()
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired items from in-memory cache.")

    def cleanup(self) -> int:
        """Remove all expired entries from the in-memory cache."""
        count = 0
        with self._lock:
            now = time.time()
            expired_keys = [k for k, v in self._memory_cache.items() if v.expiry < now]
            for key in expired_keys:
                del self._memory_cache[key]
                count += 1
            self._stats['evictions'] += count
        return count

# Create a single instance to be imported and initialized in the app factory.
cache_manager = CacheManager()