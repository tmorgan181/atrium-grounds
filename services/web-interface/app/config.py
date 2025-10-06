"""
Configuration settings for Web Interface.

Loads from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Observatory API configuration
    observatory_url: str = "http://localhost:8000"
    observatory_api_key: str | None = None  # Optional, for demo generation

    # Web interface configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded once and reused.
    """
    return Settings()


# Convenience export
settings = get_settings()
