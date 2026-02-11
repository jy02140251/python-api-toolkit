"""
Structured Logging Module.

Provides JSON-formatted structured logging for API requests
with request ID tracking and performance metrics.
"""

import json
import time
import uuid
import logging
from typing import Any, Dict, Optional
from functools import wraps


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


class APILogger:
    """
    Structured API logger with request tracking.

    Provides methods for logging API requests, responses,
    and errors with automatic performance metrics.

    Example:
        >>> api_logger = APILogger("my-api")
        >>> api_logger.log_request("GET", "/api/users", request_id="abc-123")
        >>> api_logger.log_response("GET", "/api/users", 200, 0.045, request_id="abc-123")
    """

    def __init__(self, name: str = "api", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

    def log_request(
        self,
        method: str,
        path: str,
        request_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log an incoming API request."""
        request_id = request_id or str(uuid.uuid4())[:8]
        data = {
            "event": "request",
            "method": method,
            "path": path,
            "client_ip": client_ip,
        }
        if extra:
            data.update(extra)

        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0,
            f"{method} {path}", (), None
        )
        record.request_id = request_id
        record.extra_data = data
        self.logger.handle(record)
        return request_id

    def log_response(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        request_id: Optional[str] = None,
    ) -> None:
        """Log an API response with performance metrics."""
        level = logging.INFO if status_code < 400 else logging.WARNING
        data = {
            "event": "response",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
        }
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0,
            f"{method} {path} -> {status_code} ({duration*1000:.1f}ms)",
            (), None,
        )
        record.request_id = request_id
        record.extra_data = data
        self.logger.handle(record)

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        request_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an API error."""
        data = {"event": "error"}
        if extra:
            data.update(extra)

        record = self.logger.makeRecord(
            self.logger.name, logging.ERROR, "", 0,
            message, (), error.__traceback__ if error else None,
        )
        record.request_id = request_id
        record.extra_data = data
        self.logger.handle(record)


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure application-wide structured logging.

    Args:
        level: Log level string.
        json_format: Whether to use JSON formatting.
        log_file: Optional file path for log output.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    formatter = JSONFormatter() if json_format else logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)