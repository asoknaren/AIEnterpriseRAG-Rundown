"""Qdrant collection initialization."""

from typing import Any

from src.config import VectorApiSettings


async def ensure_collection(client: Any, settings: VectorApiSettings) -> None:
    """Create the configured collection with cosine-distance vectors if absent."""
    from qdrant_client.models import Distance, VectorParams

    if not await client.collection_exists(settings.qdrant_collection_name):
        await client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(size=settings.embedding_dimension, distance=Distance.COSINE),
        )