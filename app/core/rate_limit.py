"""Rate limiting utilities."""

import time
from collections import defaultdict

from fastapi import HTTPException, status


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000) -> None:
        """Initialize rate limiter.

        Args:
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        # Store request times by IP: {ip: [timestamps]}
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make a request.

        Args:
            client_ip: Client IP address

        Returns:
            True if allowed, False otherwise
        """
        now = time.time()
        one_minute_ago = now - 60
        one_hour_ago = now - 3600

        # Clean old requests
        self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > one_hour_ago]

        # Check minute limit
        minute_requests = [ts for ts in self.requests[client_ip] if ts > one_minute_ago]
        if len(minute_requests) >= self.requests_per_minute:
            return False

        # Check hour limit
        if len(self.requests[client_ip]) >= self.requests_per_hour:
            return False

        # Record this request
        self.requests[client_ip].append(now)
        return True

    def check_rate_limit(self, client_ip: str) -> None:
        """Check rate limit and raise exception if exceeded.

        Args:
            client_ip: Client IP address

        Raises:
            HTTPException: If rate limit exceeded
        """
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
