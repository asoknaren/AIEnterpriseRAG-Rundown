"""Tests for ingestion loader configuration."""

import pytest
from pydantic import ValidationError

from src.config import IngestionLoaderSettings


def test_default_settings_match_vector_api_contract():
    """Defaults target the local Vector API and its bounded batch endpoint."""
    config = IngestionLoaderSettings()

    assert config.vector_api_url == "http://localhost:8000"
    assert config.batch_size == 50
    assert config.request_timeout_seconds == 30.0
    assert config.max_retries == 3
    assert config.max_concurrency == 4


def test_environment_overrides_are_loaded(monkeypatch):
    """Environment variables safely override local development defaults."""
    monkeypatch.setenv("VECTOR_API_BASE_URL", "https://rag-api.internal/v1/")
    monkeypatch.setenv("BATCH_SIZE", "100")
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("MAX_RETRIES", "5")
    monkeypatch.setenv("MAX_CONCURRENCY", "8")

    config = IngestionLoaderSettings()

    assert config.vector_api_url == "https://rag-api.internal/v1"
    assert config.batch_size == 100
    assert config.request_timeout_seconds == 45.0
    assert config.max_retries == 5
    assert config.max_concurrency == 8


@pytest.mark.parametrize(
    "settings",
    [
        {"vector_api_base_url": "not-a-url"},
        {"batch_size": 0},
        {"batch_size": 501},
        {"request_timeout_seconds": 0},
        {"max_retries": -1},
        {"max_concurrency": 0},
    ],
)
def test_invalid_settings_are_rejected(settings):
    """Invalid URLs and values outside API/client limits fail at startup."""
    with pytest.raises(ValidationError):
        IngestionLoaderSettings(**settings)