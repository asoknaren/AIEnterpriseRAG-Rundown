"""Tests for Document Processor configuration settings."""

import pytest
from pydantic import ValidationError

from src.config import ProcessorSettings


def test_default_settings():
    """Verify default configuration values."""
    config = ProcessorSettings()
    assert config.ollama_base_url == "http://localhost:11434"
    assert config.ollama_generation_model == "llama3.2"
    assert config.ollama_summary_model == "llama3.2"
    assert config.ollama_qa_model == "qwen2.5:7b"
    assert config.chunk_size == 512
    assert config.chunk_overlap == 64
    assert config.similarity_threshold == 0.75
    assert config.raptor_cluster_size == 5


def test_custom_environment_overrides(monkeypatch):
    """Verify environment variable overrides."""
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://remote-ollama:11434")
    monkeypatch.setenv("OLLAMA_GENERATION_MODEL", "qwen2.5:14b")
    monkeypatch.setenv("CHUNK_SIZE", "1024")
    monkeypatch.setenv("SIMILARITY_THRESHOLD", "0.85")

    config = ProcessorSettings()
    assert config.ollama_base_url == "http://remote-ollama:11434"
    assert config.ollama_generation_model == "qwen2.5:14b"
    assert config.chunk_size == 1024
    assert config.similarity_threshold == 0.85


def test_validation_constraints():
    """Verify validation boundaries."""
    with pytest.raises(ValidationError):
        # chunk_size below minimum boundary of 64
        ProcessorSettings(chunk_size=10)

    with pytest.raises(ValidationError):
        # similarity_threshold above 1.0
        ProcessorSettings(similarity_threshold=1.5)
