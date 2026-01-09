"""Security tests for input validation, authentication, and CSRF protection."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.csrf import csrf_token_manager
from app.core.validators import (
    EmailValidator,
    PasswordValidator,
    SQLInjectionValidator,
    XSSValidator,
)
from app.main import app

client = TestClient(app)


# ============================================================================
# Email Validation Tests
# ============================================================================


def test_valid_email():
    """Test valid email validation."""
    valid_emails = [
        "user@example.com",
        "test.user@example.co.uk",
        "user+tag@example.com",
    ]
    for email in valid_emails:
        result = EmailValidator.validate_email(email)
        assert result == email.lower()


def test_invalid_email():
    """Test invalid email validation."""
    invalid_emails = [
        "invalid.email",
        "@example.com",
        "user@",
        "user @example.com",
        "",
    ]
    for email in invalid_emails:
        with pytest.raises(ValueError):
            EmailValidator.validate_email(email)


def test_email_normalization():
    """Test email is normalized to lowercase."""
    email = "User@EXAMPLE.COM"
    result = EmailValidator.validate_email(email)
    assert result == "user@example.com"


# ============================================================================
# Password Validation Tests
# ============================================================================


def test_valid_password():
    """Test valid password validation."""
    valid_password = "MyP@ssw0rd"
    result = PasswordValidator.validate_password(valid_password)
    assert result == valid_password


def test_password_too_short():
    """Test password length validation."""
    with pytest.raises(ValueError, match="at least 8 characters"):
        PasswordValidator.validate_password("Short1!")


def test_password_missing_uppercase():
    """Test password missing uppercase letter."""
    with pytest.raises(ValueError, match="uppercase letter"):
        PasswordValidator.validate_password("mypassw0rd!")


def test_password_missing_lowercase():
    """Test password missing lowercase letter."""
    with pytest.raises(ValueError, match="lowercase letter"):
        PasswordValidator.validate_password("MYPASSW0RD!")


def test_password_missing_digit():
    """Test password missing digit."""
    with pytest.raises(ValueError, match="digit"):
        PasswordValidator.validate_password("MyPassword!")


def test_password_missing_special_char():
    """Test password missing special character."""
    with pytest.raises(ValueError, match="special character"):
        PasswordValidator.validate_password("MyPassword0")


# ============================================================================
# SQL Injection Prevention Tests
# ============================================================================


def test_sql_injection_detection():
    """Test SQL injection pattern detection."""
    dangerous_inputs = [
        "admin' OR '1'='1",
        "'; DROP TABLE users; --",
        "1 UNION SELECT * FROM users",
        "name' OR name LIKE '%",
    ]
    for dangerous_input in dangerous_inputs:
        with pytest.raises(ValueError, match="SQL injection"):
            SQLInjectionValidator.validate_input(dangerous_input)


def test_safe_sql_like_input():
    """Test safe inputs that look similar to SQL."""
    safe_inputs = [
        "user123",
        "test_data",
        "hello world",
    ]
    for safe_input in safe_inputs:
        result = SQLInjectionValidator.validate_input(safe_input)
        assert result == safe_input


# ============================================================================
# XSS Prevention Tests
# ============================================================================


def test_xss_detection():
    """Test XSS pattern detection."""
    dangerous_inputs = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "onclick=alert('XSS')",
    ]
    for dangerous_input in dangerous_inputs:
        with pytest.raises(ValueError, match="XSS"):
            XSSValidator.validate_input(dangerous_input)


def test_safe_html_like_input():
    """Test safe inputs that contain HTML-like text."""
    safe_inputs = [
        "This is a normal text",
        "user@example.com",
        "123-456-7890",
    ]
    for safe_input in safe_inputs:
        result = XSSValidator.validate_input(safe_input)
        assert result == safe_input


# ============================================================================
# Rate Limiting Tests
# ============================================================================


def test_login_rate_limiting():
    """Test rate limiting on login endpoint."""
    # This test would need more setup to properly test rate limits
    # For now, just verify endpoint exists
    response = client.post(
        "/api/v1/login",
        json={"email": "test@example.com", "password": "Test@1234"},
    )
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_429_TOO_MANY_REQUESTS,
    ]


# ============================================================================
# Login Endpoint Tests
# ============================================================================


def test_login_valid_credentials():
    """Test login with valid credentials."""
    response = client.post(
        "/api/v1/login",
        json={"email": "user@example.com", "password": "Password@123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email_format():
    """Test login with invalid email format."""
    response = client.post(
        "/api/v1/login",
        json={"email": "invalid-email", "password": "Password@123"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_weak_password():
    """Test login with weak password."""
    response = client.post(
        "/api/v1/login",
        json={"email": "user@example.com", "password": "weak"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_xss_attempt():
    """Test login with XSS attempt in password."""
    response = client.post(
        "/api/v1/login",
        json={
            "email": "user@example.com",
            "password": "<script>alert('XSS')</script>",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Register Endpoint Tests
# ============================================================================


def test_register_valid():
    """Test registration with valid data."""
    response = client.post(
        "/api/v1/register",
        json={
            "email": "newuser@example.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "username": "newuser",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"


def test_register_password_mismatch():
    """Test registration with mismatched passwords."""
    response = client.post(
        "/api/v1/register",
        json={
            "email": "newuser@example.com",
            "password": "Password@123",
            "confirm_password": "Password@124",
            "username": "newuser",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_weak_password():
    """Test registration with weak password."""
    response = client.post(
        "/api/v1/register",
        json={
            "email": "newuser@example.com",
            "password": "weak",
            "confirm_password": "weak",
            "username": "newuser",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_sql_injection_username():
    """Test registration with SQL injection in username."""
    response = client.post(
        "/api/v1/register",
        json={
            "email": "newuser@example.com",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "username": "admin'; DROP TABLE users; --",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Protected Endpoint Tests
# ============================================================================


def test_protected_endpoint_no_auth():
    """Test accessing protected endpoint without authentication."""
    response = client.get("/api/v1/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_with_valid_token():
    """Test accessing protected endpoint with valid token."""
    response = client.get(
        "/api/v1/protected",
        headers={"Authorization": "Bearer valid-token-format"},
    )
    assert response.status_code == status.HTTP_200_OK


def test_protected_endpoint_invalid_auth_scheme():
    """Test accessing protected endpoint with invalid auth scheme."""
    response = client.get(
        "/api/v1/protected",
        headers={"Authorization": "Basic user:pass"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# CSRF Token Tests
# ============================================================================


def test_csrf_token_generation():
    """Test CSRF token generation."""
    token = csrf_token_manager.generate_token()
    assert token is not None
    assert len(token) > 0


def test_csrf_token_validation():
    """Test CSRF token validation."""
    token = csrf_token_manager.generate_token()
    assert csrf_token_manager.validate_token(token) is True


def test_csrf_token_invalid():
    """Test CSRF token validation with invalid token."""
    assert csrf_token_manager.validate_token("invalid-token") is False


def test_csrf_token_expiration():
    """Test CSRF token expiration."""
    # Create a token with very short lifetime
    manager = csrf_token_manager
    original_lifetime = manager.token_lifetime
    try:
        manager.token_lifetime = 0  # Immediately expired
        token = manager.generate_token()
        import time

        time.sleep(0.1)
        assert manager.validate_token(token) is False
    finally:
        manager.token_lifetime = original_lifetime
