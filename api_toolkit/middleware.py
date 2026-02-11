"""Reusable ASGI/WSGI middleware components."""

import time
import uuid
import logging
from typing import Callable, Optional, Set

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    """ASGI middleware that measures and logs request processing time."""

    def __init__(self, app, slow_request_threshold: float = 1.0):
        self.app = app
        self.slow_threshold = slow_request_threshold

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()
        request_id = str(uuid.uuid4())[:8]
        path = scope.get("path", "/")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                duration = time.perf_counter() - start
                extra_headers = [
                    (b"x-request-id", request_id.encode()),
                    (b"x-response-time", f"{duration:.4f}".encode()),
                ]
                message["headers"] = list(message.get("headers", [])) + extra_headers
                if duration > self.slow_threshold:
                    logger.warning(f"[{request_id}] Slow request: {path} took {duration:.3f}s")
                else:
                    logger.info(f"[{request_id}] {path} completed in {duration:.3f}s")
            await send(message)

        await self.app(scope, receive, send_wrapper)


class CORSMiddleware:
    """Simple CORS middleware for ASGI applications."""

    def __init__(
        self,
        app,
        allow_origins: Set[str] = None,
        allow_methods: Set[str] = None,
        allow_headers: Set[str] = None,
        max_age: int = 86400,
    ):
        self.app = app
        self.allow_origins = allow_origins or {"*"}
        self.allow_methods = allow_methods or {"GET", "POST", "PUT", "DELETE", "OPTIONS"}
        self.allow_headers = allow_headers or {"*"}
        self.max_age = max_age

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        origin = headers.get(b"origin", b"").decode()

        if scope.get("method") == "OPTIONS":
            response_headers = [
                (b"access-control-allow-origin", origin.encode() if origin in self.allow_origins or "*" in self.allow_origins else b""),
                (b"access-control-allow-methods", ", ".join(self.allow_methods).encode()),
                (b"access-control-allow-headers", ", ".join(self.allow_headers).encode()),
                (b"access-control-max-age", str(self.max_age).encode()),
            ]
            await send({"type": "http.response.start", "status": 204, "headers": response_headers})
            await send({"type": "http.response.body", "body": b""})
            return

        await self.app(scope, receive, send)