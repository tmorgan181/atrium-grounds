"""Configuration management using environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    # Database Configuration
    database_url: str = "sqlite:///./data/observatory.db"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "observer"

    # Security Configuration
    api_key_salt: str = "change-this-in-production"

    # Rate Limiting (requests per minute)
    # Note: Increased limits for better DX. See specs/005-adjust-api-key-limits.md
    rate_limit_public: int = 100  # 10x increase - usable for exploration
    rate_limit_api_key: int = 1000  # 16x increase - real development use
    rate_limit_partner: int = 5000  # 8x increase - enterprise scale

    # TTL Configuration (days)
    ttl_results: int = 30
    ttl_metadata: int = 90

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Analysis Configuration
    max_conversation_length: int = 10000
    analysis_timeout: int = 30
    max_batch_size: int = 1000
    max_queue_size: int = 10000  # Maximum number of jobs in queue


# Global settings instance
settings = Settings()
