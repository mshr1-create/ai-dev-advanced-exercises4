"""Test error handling and exception classes."""

from fastapi import status
from fastapi.testclient import TestClient

from app.core.errors import (
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.main import app

client = TestClient(app)


def test_validation_error_format():
    """Test ValidationError creates correct error response."""
    error = ValidationError(detail="Invalid input", errors={"field": "error message"})
    assert error.status_code == status.HTTP_400_BAD_REQUEST
    assert error.title == "Validation Error"
    assert error.detail == "Invalid input"
    assert error.errors == {"field": "error message"}


def test_not_found_error_format():
    """Test NotFoundError creates correct error response."""
    error = NotFoundError(resource="Product", resource_id="123")
    assert error.status_code == status.HTTP_404_NOT_FOUND
    assert error.title == "Not Found"
    assert "Product" in error.detail
    assert "123" in error.detail


def test_conflict_error_format():
    """Test ConflictError creates correct error response."""
    error = ConflictError(detail="Resource already exists")
    assert error.status_code == status.HTTP_409_CONFLICT
    assert error.title == "Conflict"


def test_unauthorized_error_format():
    """Test UnauthorizedError creates correct error response."""
    error = UnauthorizedError()
    assert error.status_code == status.HTTP_401_UNAUTHORIZED
    assert error.title == "Unauthorized"


def test_forbidden_error_format():
    """Test ForbiddenError creates correct error response."""
    error = ForbiddenError()
    assert error.status_code == status.HTTP_403_FORBIDDEN
    assert error.title == "Forbidden"


def test_internal_server_error_format():
    """Test InternalServerError creates correct error response."""
    error = InternalServerError()
    assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert error.title == "Internal Server Error"
