"""Factory for selecting the configured embedding provider."""

from typing import Any

from src.config import VectorApiSettings
from src.embeddings.base import BaseEmbeddingService
from src.embeddings.fastembed_embed import FastEmbedService
from src.embeddings.ollama_embed import OllamaEmbeddingService
from src.embeddings.openai_embed import OpenAIEmbeddingService


class EmbeddingFactory:
    """Create embedding services from the Vector API configuration."""

    @staticmethod
    def create(settings: VectorApiSettings, client: Any | None = None) -> BaseEmbeddingService:
        """Instantiate the provider named by ``settings.embedding_provider``."""
        provider = settings.embedding_provider
        if provider == "ollama":
            return OllamaEmbeddingService(
                model=settings.embedding_model,
                dimension=settings.embedding_dimension,
                base_url=settings.ollama_base_url,
                client=client,
            )
        if provider == "fastembed":
            return FastEmbedService(
                model=settings.embedding_model,
                dimension=settings.embedding_dimension,
                client=client,
            )
        if provider == "openai":
            return OpenAIEmbeddingService(
                model=settings.embedding_model,
                dimension=settings.embedding_dimension,
                api_key=settings.openai_api_key,
                client=client,
            )
        raise ValueError(f"Unsupported embedding provider: {provider}")