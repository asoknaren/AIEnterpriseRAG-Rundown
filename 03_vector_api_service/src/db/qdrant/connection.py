"""Async Qdrant client lifecycle management."""

from typing import Any

from src.config import VectorApiSettings


class QdrantConnection:
    """Create and close the service's asynchronous Qdrant client."""

    def __init__(self, settings: VectorApiSettings) -> None:
        self._settings = settings
        self.client: Any | None = None

    async def connect(self) -> Any:
        """Create the client on first use and return it."""
        if self.client is None:
            from qdrant_client import AsyncQdrantClient

            self.client = AsyncQdrantClient(url=self._settings.qdrant_url, api_key=self._settings.qdrant_api_key)
        return self.client

    async def close(self) -> None:
        """Close the active Qdrant client, if any."""
        if self.client is not None:
            await self.client.close()
            self.client = None