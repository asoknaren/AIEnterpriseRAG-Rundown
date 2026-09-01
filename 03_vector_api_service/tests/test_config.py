"""Tests for Vector API settings parsing and validation."""

import pytest
from pydantic import ValidationError

from src.config import VectorApiSettings


def test_default_settings_match_local_service_configuration():
    """Defaults match the repository's Docker Compose services."""
    config = VectorApiSettings()
    assert config.vector_db_backend == "postgres"
    assert config.postgres_dsn == "postgresql://postgres:postgrespassword@localhost:5432/ragdb"
    assert config.qdrant_url == "http://localhost:6333"
    assert config.embedding_provider == "ollama"
    assert config.embedding_dimension == 768


def test_environment_overrides_support_qdrant_and_openai(monkeypatch):
    """Settings accept environment configuration for alternative backends."""
    monkeypatch.setenv("VECTOR_DB_BACKEND", "qdrant")
    monkeypatch.setenv("QDRANT_HOST", "qdrant.internal")
    monkeypatch.setenv("QDRANT_PORT", "6334")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDING_DIMENSION", "1536")

    config = VectorApiSettings()

    assert config.vector_db_backend == "qdrant"
    assert config.qdrant_url == "http://qdrant.internal:6334"
    assert config.embedding_provider == "openai"
    assert config.embedding_dimension == 1536


@pytest.mark.parametrize(
    "settings",
    [
        {"vector_db_backend": "unsupported"},
        {"embedding_provider": "unsupported"},
        {"postgres_min_connections": 21, "postgres_max_connections": 20},
        {"postgres_port": 0},
    ],
)
def test_invalid_settings_are_rejected(settings):
    """Backend values, pool limits, and ports are validated at startup."""
    with pytest.raises(ValidationError):
        VectorApiSettings(**settings)