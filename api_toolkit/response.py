"""Standardized API response builders."""

from typing import Any, Optional, Dict, List
from datetime import datetime
from http import HTTPStatus


class ApiResponse:
    """Builder for consistent API responses."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        response = {
            "success": True,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if data is not None:
            response["data"] = data
        if meta:
            response["meta"] = meta
        return response

    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = 500,
        errors: Optional[List[Dict]] = None,
        error_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = {
            "success": False,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if error_code:
            response["error_code"] = error_code
        if errors:
            response["errors"] = errors
        return response

    @staticmethod
    def created(data: Any = None, message: str = "Resource created") -> Dict[str, Any]:
        return ApiResponse.success(data=data, message=message, status_code=201)

    @staticmethod
    def no_content() -> Dict[str, Any]:
        return {"status_code": 204}

    @staticmethod
    def not_found(resource: str = "Resource") -> Dict[str, Any]:
        return ApiResponse.error(
            message=f"{resource} not found",
            status_code=404,
            error_code="NOT_FOUND",
        )

    @staticmethod
    def validation_error(errors: List[Dict]) -> Dict[str, Any]:
        return ApiResponse.error(
            message="Validation failed",
            status_code=422,
            errors=errors,
            error_code="VALIDATION_ERROR",
        )

    @staticmethod
    def unauthorized(message: str = "Authentication required") -> Dict[str, Any]:
        return ApiResponse.error(message=message, status_code=401, error_code="UNAUTHORIZED")

    @staticmethod
    def forbidden(message: str = "Permission denied") -> Dict[str, Any]:
        return ApiResponse.error(message=message, status_code=403, error_code="FORBIDDEN")