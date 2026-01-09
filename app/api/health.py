"""Health check endpoints."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(description="Application status")
    app_name: str = Field(description="Application name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Runtime environment")


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint.

    Returns application status and basic information.
    Demonstrates correlation ID logging.
    """
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.info(
        "health_check_requested",
        correlation_id=correlation_id,
        environment=settings.node_env,
    )

    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.node_env,
    )


@router.get("/")
async def root(request: Request) -> dict[str, str]:
    """Root endpoint.

    Returns welcome message with correlation ID.
    """
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.info("root_endpoint_accessed", correlation_id=correlation_id)

    return {
        "message": "Welcome to Sweets EC API",
        "correlation_id": correlation_id or "unknown",
    }
