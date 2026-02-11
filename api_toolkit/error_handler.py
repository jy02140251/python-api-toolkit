"""
Error Handler Module.

Provides standardized API error response formatting
and common HTTP error classes.
"""

from typing import Any, Dict, Optional, List


class APIError(Exception):
    """
    Base API error with HTTP status code and structured response.

    Args:
        message: Human-readable error message.
        status_code: HTTP status code.
        error_code: Machine-readable error code.
        details: Additional error details.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERR_{status_code}"
        self.details = details
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to a JSON-serializable dictionary."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "status": self.status_code,
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        return response


class NotFoundError(APIError):
    """Resource not found (404)."""
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class UnauthorizedError(APIError):
    """Authentication required (401)."""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenError(APIError):
    """Insufficient permissions (403)."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class BadRequestError(APIError):
    """Invalid request data (400)."""
    def __init__(self, message: str = "Invalid request", errors: Optional[List[Dict]] = None):
        super().__init__(
            message,
            status_code=400,
            error_code="BAD_REQUEST",
            details={"validation_errors": errors} if errors else None,
        )


class ConflictError(APIError):
    """Resource conflict (409)."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409, error_code="CONFLICT")


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            "Rate limit exceeded",
            status_code=429,
            error_code="RATE_LIMITED",
            details={"retry_after_seconds": retry_after},
        )


def error_response(
    message: str,
    status_code: int = 500,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        message: Error message.
        status_code: HTTP status code.
        error_code: Machine-readable error code.
        details: Additional context.

    Returns:
        Formatted error response dictionary.
    """
    return APIError(
        message=message,
        status_code=status_code,
        error_code=error_code,
        details=details,
    ).to_dict()