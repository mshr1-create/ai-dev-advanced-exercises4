"""FastAPI application factory and main entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import AppException, ErrorDetail
from app.core.logging import configure_logging, get_logger
from app.core.middleware import CorrelationIdMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info("application_startup", app_name=settings.app_name, version=settings.app_version)
    yield
    # Shutdown
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    # Configure logging first
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add correlation ID middleware
    app.add_middleware(CorrelationIdMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Register routes
    register_routes(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers.

    Args:
        app: FastAPI application
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle application exceptions with RFC 7807 format."""
        correlation_id = getattr(request.state, "correlation_id", None)

        error_detail = ErrorDetail(
            type=exc.error_type,
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            correlation_id=correlation_id,
            errors=exc.errors,
        )

        logger.error(
            "application_error",
            error_type=exc.error_type,
            title=exc.title,
            detail=exc.detail,
            status_code=exc.status_code,
            correlation_id=correlation_id,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_detail.model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI validation errors."""
        correlation_id = getattr(request.state, "correlation_id", None)

        # Format validation errors
        errors = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors[field] = error["msg"]

        error_detail = ErrorDetail(
            type="/errors/validation-error",
            title="Validation Error",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request validation failed",
            correlation_id=correlation_id,
            errors=errors,
        )

        logger.warning(
            "validation_error",
            errors=errors,
            correlation_id=correlation_id,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_detail.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        correlation_id = getattr(request.state, "correlation_id", None)

        error_detail = ErrorDetail(
            type="/errors/internal-server-error",
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred" if not settings.debug else str(exc),
            correlation_id=correlation_id,
        )

        logger.exception(
            "unexpected_error",
            error=str(exc),
            correlation_id=correlation_id,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_detail.model_dump(exclude_none=True),
        )


def register_routes(app: FastAPI) -> None:
    """Register application routes.

    Args:
        app: FastAPI application
    """
    from app.api import health

    app.include_router(health.router, tags=["health"])


# Create application instance
app = create_app()
