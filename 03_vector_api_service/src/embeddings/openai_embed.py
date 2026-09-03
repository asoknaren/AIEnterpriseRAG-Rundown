"""OpenAI embedding provider."""

from typing import Any

from src.embeddings.base import BaseEmbeddingService


class OpenAIEmbeddingService(BaseEmbeddingService):
    """Generate embeddings through the OpenAI asynchronous client."""

    def __init__(self, model: str, dimension: int, api_key: str | None, client: Any | None = None) -> None:
        super().__init__(model, dimension)
        if client is None:
            if not api_key:
                raise ValueError("openai_api_key is required when embedding_provider is 'openai'.")
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=api_key)
        self.client = client

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(model=self.model, input=texts)
        embeddings = [item.embedding for item in response.data]
        return self.validate_embeddings(embeddings, len(texts))