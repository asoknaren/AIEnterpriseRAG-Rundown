"""Validated configuration for the Vector API service."""

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EmbeddingProvider = Literal["ollama", "fastembed", "openai"]
EmbeddingModel = Literal[
    "nomic-embed-text",
    "mxbai-embed-large",
    "BAAI/bge-small-en-v1.5",
    "BAAI/bge-base-en-v1.5",
    "text-embedding-3-small",
    "text-embedding-3-large",
]

EMBEDDING_DIMENSIONS: dict[EmbeddingProvider, dict[EmbeddingModel, int]] = {
    "ollama": {"nomic-embed-text": 768, "mxbai-embed-large": 1024},
    "fastembed": {
        "BAAI/bge-small-en-v1.5": 384,
        "BAAI/bge-base-en-v1.5": 768,
    },
    "openai": {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    },
}


class VectorApiSettings(BaseSettings):
    """Database and embedding settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    vector_db_backend: Literal["postgres", "qdrant"] = "postgres"

    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "ragdb"
    postgres_user: str = "postgres"
    postgres_password: str = "postgrespassword"
    postgres_min_connections: int = Field(default=5, ge=1)
    postgres_max_connections: int = Field(default=20, ge=1)

    qdrant_host: str = "localhost"
    qdrant_port: int = Field(default=6333, ge=1, le=65535)
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "enterprise_docs_chunks"

    embedding_provider: EmbeddingProvider = "openai"
    embedding_model: EmbeddingModel = "text-embedding-3-small"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str | None = None

    @model_validator(mode="after")
    def validate_pool_limits(self) -> "VectorApiSettings":
        """Ensure the connection pool has a feasible lower and upper bound."""
        if self.postgres_min_connections > self.postgres_max_connections:
            raise ValueError("postgres_min_connections cannot exceed postgres_max_connections")
        if self.embedding_model not in EMBEDDING_DIMENSIONS[self.embedding_provider]:
            raise ValueError(
                f"Embedding model '{self.embedding_model}' is not supported by provider "
                f"'{self.embedding_provider}'."
            )
        return self

    @property
    def embedding_dimension(self) -> int:
        """Return the native vector dimension of the selected embedding model."""
        return EMBEDDING_DIMENSIONS[self.embedding_provider][self.embedding_model]

    @property
    def postgres_dsn(self) -> str:
        """Build the asyncpg-compatible PostgreSQL connection string."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def qdrant_url(self) -> str:
        """Build the Qdrant base URL from its host and port."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


settings = VectorApiSettings()