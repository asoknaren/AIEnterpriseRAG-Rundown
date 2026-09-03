"""Shared contract for vector embedding providers."""

from abc import ABC, abstractmethod


class EmbeddingServiceError(RuntimeError):
    """Raised when an embedding provider returns an invalid result."""


class BaseEmbeddingService(ABC):
    """Asynchronous interface implemented by every embedding provider."""

    def __init__(self, model: str, dimension: int) -> None:
        self.model = model
        self.dimension = dimension

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Create one embedding vector for each supplied text."""

    async def embed_query(self, text: str) -> list[float]:
        """Create a single vector for a search query."""
        return (await self.embed_texts([text]))[0]

    def validate_embeddings(self, embeddings: list[list[float]], expected_count: int) -> list[list[float]]:
        """Ensure provider output has one correctly sized vector per input."""
        if len(embeddings) != expected_count:
            raise EmbeddingServiceError(
                f"Expected {expected_count} embedding(s), received {len(embeddings)}."
            )
        for embedding in embeddings:
            if len(embedding) != self.dimension:
                raise EmbeddingServiceError(
                    f"Expected embedding dimension {self.dimension}, received {len(embedding)}."
                )
        return embeddings