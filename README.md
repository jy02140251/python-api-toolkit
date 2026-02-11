# Python API Toolkit

A comprehensive Python toolkit for building robust, production-ready APIs. Provides reusable utilities for rate limiting, retry logic, JWT authentication, request validation, error handling, caching, and structured logging.

## Features

- **Rate Limiter**: Token bucket and sliding window rate limiting
- **Retry**: Configurable retry with exponential backoff and jitter
- **JWT Auth**: JWT token generation, validation, and middleware
- **Validator**: Request payload validation with custom rules
- **Error Handler**: Standardized API error responses
- **Cache**: In-memory and Redis-backed caching with TTL
- **Logger**: Structured JSON logging for API requests

## Installation

```bash
pip install python-api-toolkit
# or from source
git clone https://github.com/jy02140251/python-api-toolkit.git
cd python-api-toolkit
pip install -e .
```

## Quick Start

```python
from api_toolkit import RateLimiter, retry, JWTAuth, RequestValidator

# Rate limiting
limiter = RateLimiter(max_requests=100, window_seconds=60)
if limiter.allow("client-ip"):
    process_request()

# Retry with backoff
@retry(max_attempts=3, backoff_factor=2.0)
def call_external_api():
    return requests.get("https://api.example.com/data")

# JWT Authentication
auth = JWTAuth(secret_key="your-secret")
token = auth.create_token({"user_id": "123", "role": "admin"})
payload = auth.verify_token(token)
```

## Modules

| Module | Description |
|--------|-------------|
| `rate_limiter` | Token bucket rate limiting |
| `retry` | Retry decorator with backoff |
| `jwt_auth` | JWT token management |
| `validator` | Request validation |
| `error_handler` | Standardized error responses |
| `cache` | In-memory and Redis caching |
| `logger` | Structured JSON logging |

## License

MIT License