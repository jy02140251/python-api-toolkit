"""
Python API Toolkit.

A comprehensive toolkit for building production-ready Python APIs
with rate limiting, retry logic, JWT auth, caching, and more.
"""

from api_toolkit.rate_limiter import RateLimiter, SlidingWindowLimiter
from api_toolkit.retry import retry, RetryConfig
from api_toolkit.jwt_auth import JWTAuth
from api_toolkit.validator import RequestValidator, ValidationError
from api_toolkit.error_handler import APIError, error_response
from api_toolkit.cache import Cache, RedisCache
from api_toolkit.logger import APILogger, setup_logging

__version__ = "1.0.0"

__all__ = [
    "RateLimiter",
    "SlidingWindowLimiter",
    "retry",
    "RetryConfig",
    "JWTAuth",
    "RequestValidator",
    "ValidationError",
    "APIError",
    "error_response",
    "Cache",
    "RedisCache",
    "APILogger",
    "setup_logging",
]