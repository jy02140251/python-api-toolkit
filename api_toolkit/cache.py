"""
Cache Module.

Provides in-memory and Redis-backed caching with TTL support,
key prefixing, and cache invalidation utilities.
"""

import time
import json
import logging
from typing import Any, Optional, Dict
from functools import wraps

logger = logging.getLogger(__name__)


class Cache:
    """
    In-memory cache with TTL support.

    Simple dictionary-based cache suitable for single-process
    applications or development environments.

    Args:
        default_ttl: Default time-to-live in seconds.
        max_size: Maximum number of cached items.

    Example:
        >>> cache = Cache(default_ttl=300)
        >>> cache.set("user:123", {"name": "John"})
        >>> cache.get("user:123")
        {"name": "John"}
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache. Returns None if expired or missing."""
        entry = self._store.get(key)
        if entry is None:
            return None

        if entry["expires_at"] < time.time():
            del self._store[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL override."""
        # Evict oldest entries if at capacity
        if len(self._store) >= self.max_size and key not in self._store:
            self._evict_expired()
            if len(self._store) >= self.max_size:
                oldest_key = min(self._store, key=lambda k: self._store[k]["expires_at"])
                del self._store[oldest_key]

        self._store[key] = {
            "value": value,
            "expires_at": time.time() + (ttl or self.default_ttl),
        }

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Clear all cached items."""
        self._store.clear()

    def has(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        return self.get(key) is not None

    @property
    def size(self) -> int:
        """Get current number of cached items."""
        self._evict_expired()
        return len(self._store)

    def _evict_expired(self) -> None:
        """Remove all expired entries."""
        now = time.time()
        expired = [k for k, v in self._store.items() if v["expires_at"] < now]
        for key in expired:
            del self._store[key]


class RedisCache:
    """
    Redis-backed cache with TTL support.

    Production-ready cache using Redis for distributed caching
    across multiple application instances.

    Args:
        redis_client: Redis client instance.
        prefix: Key prefix for namespacing.
        default_ttl: Default TTL in seconds.
    """

    def __init__(self, redis_client, prefix: str = "cache:", default_ttl: int = 300):
        self.redis = redis_client
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key."""
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache."""
        raw = self.redis.get(self._make_key(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in Redis cache with TTL."""
        serialized = json.dumps(value) if not isinstance(value, (str, bytes)) else value
        self.redis.setex(
            self._make_key(key),
            ttl or self.default_ttl,
            serialized,
        )

    def delete(self, key: str) -> bool:
        """Delete a key from Redis cache."""
        return bool(self.redis.delete(self._make_key(key)))

    def clear(self, pattern: str = "*") -> int:
        """Clear cache keys matching pattern."""
        keys = self.redis.keys(f"{self.prefix}{pattern}")
        if keys:
            return self.redis.delete(*keys)
        return 0


def cached(cache_instance, key_func=None, ttl=None):
    """
    Decorator for caching function results.

    Args:
        cache_instance: Cache or RedisCache instance.
        key_func: Function to generate cache key from args.
        ttl: Optional TTL override.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"

            result = cache_instance.get(cache_key)
            if result is not None:
                logger.debug("Cache hit: %s", cache_key)
                return result

            logger.debug("Cache miss: %s", cache_key)
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator