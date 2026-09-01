"""Backend repository selection."""

from typing import Any

from src.config import VectorApiSettings
from src.db.base import BaseVectorRepository
from src.db.postgres import PostgresVectorRepository
from src.db.qdrant import QdrantVectorRepository


class RepositoryFactory:
    """Resolve a repository from the configured vector database backend."""

    @staticmethod
    def create(settings: VectorApiSettings, connection: Any) -> BaseVectorRepository:
        if settings.vector_db_backend == "postgres":
            return PostgresVectorRepository(connection)
        return QdrantVectorRepository(connection, settings.qdrant_collection_name)