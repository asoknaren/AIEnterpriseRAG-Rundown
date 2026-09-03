"""FastEmbed embedding provider."""

from typing import Any

from src.embeddings.base import BaseEmbeddingService


class FastEmbedService(BaseEmbeddingService):
    """Generate in-process embeddings using a FastEmbed model."""

    def __init__(self, model: str, dimension: int, client: Any | None = None) -> None:
        super().__init__(model, dimension)
        if client is None:
            from fastembed import TextEmbedding

            client = TextEmbedding(model_name=model)
        self.client = client

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = [list(embedding) for embedding in self.client.embed(texts)]
        return self.validate_embeddings(embeddings, len(texts))