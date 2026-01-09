"""Validators for common input patterns."""

import re


class EmailValidator:
    """Email validation utilities."""

    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )

    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email address format.

        Args:
            value: Email address to validate

        Returns:
            Validated email address

        Raises:
            ValueError: If email format is invalid
        """
        if not value or len(value) > 254:
            raise ValueError("Invalid email length")
        if not EmailValidator.EMAIL_PATTERN.match(value):
            raise ValueError("Invalid email format")
        return value.lower()


class PasswordValidator:
    """Password validation utilities."""

    @staticmethod
    def validate_password(value: str) -> str:
        """Validate password strength.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            value: Password to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",.<>?/\\|`~]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class URLValidator:
    """URL validation utilities."""

    URL_PATTERN = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP address
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    @staticmethod
    def validate_url(value: str) -> str:
        """Validate URL format.

        Args:
            value: URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL format is invalid
        """
        if not URLValidator.URL_PATTERN.match(value):
            raise ValueError("Invalid URL format")
        if len(value) > 2048:
            raise ValueError("URL is too long")
        return value


class SQLInjectionValidator:
    """SQL Injection prevention utilities."""

    DANGEROUS_PATTERNS = [
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(LIKE\s+['\"]%)",
    ]

    @staticmethod
    def validate_input(value: str) -> str:
        """Validate input against SQL injection patterns.

        Args:
            value: Input to validate

        Returns:
            Validated input

        Raises:
            ValueError: If suspicious patterns are detected
        """
        value_upper = value.upper()
        for pattern in SQLInjectionValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value_upper):
                raise ValueError("Invalid input detected (potential SQL injection)")
        return value


class XSSValidator:
    """XSS prevention utilities."""

    DANGEROUS_TAGS = ["<script", "<iframe", "<img", "onerror=", "onload=", "onclick="]

    @staticmethod
    def validate_input(value: str) -> str:
        """Validate input against XSS patterns.

        Args:
            value: Input to validate

        Returns:
            Validated input

        Raises:
            ValueError: If dangerous HTML/JS patterns are detected
        """
        value_lower = value.lower()
        for tag in XSSValidator.DANGEROUS_TAGS:
            if tag in value_lower:
                raise ValueError("Invalid input detected (potential XSS)")
        return value
