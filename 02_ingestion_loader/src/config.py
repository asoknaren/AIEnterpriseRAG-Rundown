"""Validated configuration for the ingestion loader."""

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionLoaderSettings(BaseSettings):
    """Loader settings sourced from environment variables or a local .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    vector_api_base_url: AnyHttpUrl = "http://localhost:8000"
    batch_size: int = Field(default=50, ge=1, le=500)
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff_seconds: float = Field(default=0.5, gt=0)
    max_concurrency: int = Field(default=4, ge=1, le=32)

    @property
    def vector_api_url(self) -> str:
        """Return the API URL without a trailing slash for endpoint construction."""
        return str(self.vector_api_base_url).rstrip("/")


settings = IngestionLoaderSettings()