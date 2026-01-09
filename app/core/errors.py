"""Unified error handling and exception classes.

Implements RFC 7807 Problem Details for HTTP APIs format.
"""

from typing import Any

from fastapi import status
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail following RFC 7807 Problem Details format."""

    type: str = Field(
        description="URI reference identifying the problem type",
        examples=["about:blank", "/errors/validation-error"],
    )
    title: str = Field(description="Short, human-readable summary of the problem")
    status: int = Field(description="HTTP status code", ge=100, le=599)
    detail: str | None = Field(
        default=None, description="Human-readable explanation specific to this occurrence"
    )
    instance: str | None = Field(
        default=None, description="URI reference identifying the specific occurrence"
    )
    correlation_id: str | None = Field(
        default=None, description="Request correlation ID for tracing"
    )
    errors: dict[str, Any] | None = Field(
        default=None, description="Additional error details (e.g., validation errors)"
    )


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        title: str,
        detail: str | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type: str = "about:blank",
        errors: dict[str, Any] | None = None,
    ) -> None:
        """Initialize application exception.

        Args:
            title: Short error summary
            detail: Detailed error message
            status_code: HTTP status code
            error_type: Error type URI
            errors: Additional error details
        """
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.error_type = error_type
        self.errors = errors
        super().__init__(detail or title)


class ValidationError(AppException):
    """Validation error (400 Bad Request)."""

    def __init__(
        self, detail: str = "Validation failed", errors: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            title="Validation Error",
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="/errors/validation-error",
            errors=errors,
        )


class NotFoundError(AppException):
    """Resource not found error (404 Not Found)."""

    def __init__(self, resource: str, resource_id: str | int | None = None) -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            title="Not Found",
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="/errors/not-found",
        )


class ConflictError(AppException):
    """Resource conflict error (409 Conflict)."""

    def __init__(self, detail: str = "Resource conflict occurred") -> None:
        super().__init__(
            title="Conflict",
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_type="/errors/conflict",
        )


class UnauthorizedError(AppException):
    """Authentication error (401 Unauthorized)."""

    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(
            title="Unauthorized",
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="/errors/unauthorized",
        )


class ForbiddenError(AppException):
    """Authorization error (403 Forbidden)."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(
            title="Forbidden",
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="/errors/forbidden",
        )


class InternalServerError(AppException):
    """Internal server error (500)."""

    def __init__(self, detail: str = "An internal server error occurred") -> None:
        super().__init__(
            title="Internal Server Error",
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="/errors/internal-server-error",
        )
