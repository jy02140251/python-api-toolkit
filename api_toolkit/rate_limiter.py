"""
Rate Limiter Module.

Implements token bucket and sliding window rate limiting
algorithms for controlling API request rates.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TokenBucket:
    """Token bucket for a single client."""
    tokens: float
    max_tokens: int
    refill_rate: float
    last_refill: float = field(default_factory=time.time)


class RateLimiter:
    """
    Token bucket rate limiter.

    Allows a configurable number of requests per time window
    with smooth token refilling.

    Args:
        max_requests: Maximum requests allowed in the window.
        window_seconds: Time window in seconds.
    
    Example:
        >>> limiter = RateLimiter(max_requests=100, window_seconds=60)
        >>> limiter.allow("client-1")  # True
        >>> limiter.get_remaining("client-1")  # 99
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.refill_rate = max_requests / window_seconds
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def allow(self, client_id: str) -> bool:
        """
        Check if a request from the client should be allowed.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            True if request is allowed, False if rate limited.
        """
        with self._lock:
            bucket = self._get_or_create_bucket(client_id)
            self._refill(bucket)

            if bucket.tokens >= 1:
                bucket.tokens -= 1
                return True
            return False

    def get_remaining(self, client_id: str) -> int:
        """Get remaining tokens for a client."""
        with self._lock:
            bucket = self._buckets.get(client_id)
            if not bucket:
                return self.max_requests
            self._refill(bucket)
            return int(bucket.tokens)

    def get_reset_time(self, client_id: str) -> float:
        """Get seconds until the bucket is fully refilled."""
        with self._lock:
            bucket = self._buckets.get(client_id)
            if not bucket:
                return 0.0
            tokens_needed = self.max_requests - bucket.tokens
            return tokens_needed / self.refill_rate if self.refill_rate > 0 else 0.0

    def reset(self, client_id: str) -> None:
        """Reset rate limit for a specific client."""
        with self._lock:
            self._buckets.pop(client_id, None)

    def _get_or_create_bucket(self, client_id: str) -> TokenBucket:
        """Get existing bucket or create a new one."""
        if client_id not in self._buckets:
            self._buckets[client_id] = TokenBucket(
                tokens=float(self.max_requests),
                max_tokens=self.max_requests,
                refill_rate=self.refill_rate,
            )
        return self._buckets[client_id]

    def _refill(self, bucket: TokenBucket) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket.last_refill
        new_tokens = elapsed * bucket.refill_rate
        bucket.tokens = min(bucket.max_tokens, bucket.tokens + new_tokens)
        bucket.last_refill = now


class SlidingWindowLimiter:
    """
    Sliding window rate limiter using timestamp tracking.
    
    More accurate than token bucket for bursty traffic patterns.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()

    def allow(self, client_id: str) -> bool:
        """Check if a request should be allowed within the sliding window."""
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            if client_id not in self._requests:
                self._requests[client_id] = []

            # Remove expired timestamps
            self._requests[client_id] = [
                ts for ts in self._requests[client_id] if ts > cutoff
            ]

            if len(self._requests[client_id]) < self.max_requests:
                self._requests[client_id].append(now)
                return True
            return False