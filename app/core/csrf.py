"""CSRF protection utilities."""

import secrets
import time

from fastapi import HTTPException, Request, status


class CSRFTokenManager:
    """CSRF token generation and validation."""

    def __init__(self, token_lifetime: int = 3600) -> None:
        """Initialize CSRF token manager.

        Args:
            token_lifetime: Token lifetime in seconds (default: 1 hour)
        """
        self.token_lifetime = token_lifetime
        self.tokens: dict[str, tuple[str, float]] = {}

    def generate_token(self) -> str:
        """Generate a new CSRF token.

        Returns:
            Generated CSRF token
        """
        # Generate random token
        token = secrets.token_urlsafe(32)
        # Store with timestamp
        self.tokens[token] = (token, time.time())
        return token

    def validate_token(self, token: str) -> bool:
        """Validate CSRF token.

        Args:
            token: Token to validate

        Returns:
            True if token is valid, False otherwise
        """
        if token not in self.tokens:
            return False

        _, issued_at = self.tokens[token]
        if time.time() - issued_at > self.token_lifetime:
            # Token expired
            del self.tokens[token]
            return False

        return True

    def verify_token(self, token: str) -> None:
        """Verify CSRF token and raise exception if invalid.

        Args:
            token: Token to verify

        Raises:
            HTTPException: If token is invalid or expired
        """
        if not self.validate_token(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired CSRF token",
            )

    def cleanup_expired(self) -> None:
        """Clean up expired tokens."""
        now = time.time()
        expired_tokens = [
            token
            for token, (_, issued_at) in self.tokens.items()
            if now - issued_at > self.token_lifetime
        ]
        for token in expired_tokens:
            del self.tokens[token]


# Global CSRF token manager instance
csrf_token_manager = CSRFTokenManager(token_lifetime=3600)


def get_csrf_token(request: Request) -> str:
    """Get or generate CSRF token for request.

    Args:
        request: HTTP request

    Returns:
        CSRF token
    """
    # Check if token is already in session/cookie
    csrf_token = request.headers.get("X-CSRF-Token")
    if csrf_token and csrf_token_manager.validate_token(csrf_token):
        return csrf_token

    # Generate new token
    return csrf_token_manager.generate_token()


def verify_csrf_token(token: str) -> None:
    """Verify CSRF token.

    Args:
        token: Token to verify

    Raises:
        HTTPException: If token is invalid
    """
    csrf_token_manager.verify_token(token)
