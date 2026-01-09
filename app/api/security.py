"""Security-aware API endpoints."""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.logging import get_logger
from app.core.rate_limit import rate_limiter
from app.core.security import Token, create_access_token
from app.core.validators import (
    EmailValidator,
    PasswordValidator,
    SQLInjectionValidator,
    XSSValidator,
)

router = APIRouter(prefix="/api/v1", tags=["security"])
logger = get_logger(__name__)


class LoginRequest(BaseModel):
    """Login request with validated inputs."""

    email: str = Field(..., min_length=5, max_length=254, description="User email")
    password: str = Field(..., min_length=8, description="User password")

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        """Validate email format."""
        return EmailValidator.validate_email(v)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        """Validate password format (basic XSS check)."""
        return XSSValidator.validate_input(v)


class RegisterRequest(BaseModel):
    """Registration request with strong validation."""

    email: str = Field(..., min_length=5, max_length=254, description="User email")
    password: str = Field(..., description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    username: str = Field(..., min_length=3, max_length=50, description="Username")

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        """Validate email format."""
        return EmailValidator.validate_email(v)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        """Validate password strength."""
        return PasswordValidator.validate_password(v)

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v: str) -> str:
        """Validate username (no SQL injection/XSS)."""
        v = SQLInjectionValidator.validate_input(v)
        return XSSValidator.validate_input(v)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password_field(cls, v: str) -> str:
        """Validate confirm password (basic checks)."""
        return XSSValidator.validate_input(v)

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "RegisterRequest":
        """Validate that passwords match."""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(request: Request, credentials: LoginRequest) -> dict[str, str]:
    """Login endpoint with rate limiting and input validation.

    Args:
        request: HTTP request
        credentials: Login credentials (email, password)

    Returns:
        Access token

    Raises:
        HTTPException: If rate limited, credentials invalid, or input invalid
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit
    rate_limiter.check_rate_limit(client_ip)

    # Log login attempt
    logger.info(
        "login_attempt",
        email=credentials.email,
        client_ip=client_ip,
    )

    # TODO: In production, verify against actual database
    # For now, accept any email/password combination as demo
    if not credentials.email or not credentials.password:
        logger.warning(
            "login_failed",
            email=credentials.email,
            reason="empty_credentials",
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create access token
    access_token = create_access_token(data={"sub": credentials.email})

    logger.info(
        "login_success",
        email=credentials.email,
        client_ip=client_ip,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, user_data: RegisterRequest) -> dict[str, str]:
    """Register endpoint with strong input validation.

    Args:
        request: HTTP request
        user_data: User registration data

    Returns:
        Success message

    Raises:
        HTTPException: If rate limited or input validation fails
    """
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit (stricter for registration)
    try:
        rate_limiter.check_rate_limit(client_ip)
    except HTTPException:
        logger.warning(
            "registration_rate_limited",
            client_ip=client_ip,
        )
        raise

    # Log registration attempt
    logger.info(
        "registration_attempt",
        email=user_data.email,
        username=user_data.username,
        client_ip=client_ip,
    )

    # TODO: In production, save to database with hashed password
    # from app.core.security import hash_password
    # hashed_password = hash_password(user_data.password)

    logger.info(
        "registration_success",
        email=user_data.email,
        username=user_data.username,
        client_ip=client_ip,
    )

    return {
        "message": "Registration successful",
        "email": user_data.email,
        "username": user_data.username,
    }


@router.get("/protected", status_code=status.HTTP_200_OK)
async def protected_endpoint(request: Request) -> dict[str, str]:
    """Protected endpoint requiring authentication.

    Args:
        request: HTTP request

    Returns:
        Protected data

    Raises:
        HTTPException: If not authenticated
    """
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning(
            "protected_access_unauthorized",
            reason="missing_auth_header",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract and verify token
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")

        # In production, use verify_token from security module
        # token_data = verify_token(token)
        # user_id = token_data.sub

        logger.info(
            "protected_access_granted",
            token_scheme=scheme,
        )

        return {
            "message": "Access granted to protected resource",
            "status": "authenticated",
        }
    except (ValueError, IndexError) as e:
        logger.warning(
            "protected_access_unauthorized",
            reason="invalid_auth_format",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
