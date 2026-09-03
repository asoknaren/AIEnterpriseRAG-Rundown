"""Ollama embedding provider."""

from typing import Any

from src.embeddings.base import BaseEmbeddingService


class OllamaEmbeddingService(BaseEmbeddingService):
    """Generate local embeddings through Ollama's asynchronous client."""

    def __init__(self, model: str, dimension: int, base_url: str, client: Any | None = None) -> None:
        super().__init__(model, dimension)
        if client is None:
            from ollama import AsyncClient

            client = AsyncClient(host=base_url)
        self.client = client

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embed(model=self.model, input=texts)
        embeddings = response["embeddings"] if isinstance(response, dict) else response.embeddings
        return self.validate_embeddings(embeddings, len(texts))