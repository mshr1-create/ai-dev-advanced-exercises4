"""Application configuration using pydantic-settings."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Sweets EC API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    node_env: Literal["development", "production", "test"] = Field(
        default="development", description="Runtime environment"
    )
    port: int = Field(default=3000, description="Application port")
    debug: bool = Field(default=False, description="Debug mode")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Log level"
    )
    log_file_path: str | None = Field(default=None, description="Log file path (optional)")
    log_json_format: bool = Field(
        default=True, description="Use JSON format for structured logging"
    )

    # CORS (for future frontend integration)
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Feature Flags
    enable_ai_recommendations: bool = Field(
        default=False, description="Enable AI recommendation features"
    )
    enable_realtime_inventory: bool = Field(
        default=False, description="Enable real-time inventory sync"
    )


# Global settings instance
settings = Settings()
