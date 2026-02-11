"""Tests for the Rate Limiter module."""

import time
import pytest
from api_toolkit.rate_limiter import RateLimiter, SlidingWindowLimiter


class TestRateLimiter:
    """Tests for token bucket rate limiter."""

    def test_allows_within_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.allow("client-1") is True

    def test_blocks_over_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.allow("client-1")
        assert limiter.allow("client-1") is False

    def test_different_clients_independent(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        assert limiter.allow("client-1") is True
        assert limiter.allow("client-2") is True

    def test_get_remaining(self):
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        limiter.allow("client-1")
        assert limiter.get_remaining("client-1") == 9

    def test_reset(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.allow("client-1")
        assert limiter.allow("client-1") is False
        limiter.reset("client-1")
        assert limiter.allow("client-1") is True


class TestSlidingWindowLimiter:
    """Tests for sliding window rate limiter."""

    def test_allows_within_window(self):
        limiter = SlidingWindowLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            assert limiter.allow("client-1") is True
        assert limiter.allow("client-1") is False