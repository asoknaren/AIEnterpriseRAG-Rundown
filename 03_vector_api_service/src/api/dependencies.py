"""FastAPI dependencies backed by application state."""

from fastapi import Request

from src.db.base import BaseVectorRepository
from src.embeddings.base import BaseEmbeddingService


def get_repository(request: Request) -> BaseVectorRepository:
    """Return the repository initialized during application startup."""
    return request.app.state.repository


def get_embedding_service(request: Request) -> BaseEmbeddingService:
    """Return the embedding service initialized during application startup."""
    return request.app.state.embedding_service