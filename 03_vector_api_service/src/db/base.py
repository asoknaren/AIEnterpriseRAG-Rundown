"""Backend-neutral vector repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.schemas import (
    ChunkCreate,
    DocumentCreate,
    DocumentResponse,
    SearchQuery,
    SearchResult,
)


class BaseVectorRepository(ABC):
    """Persistence contract shared by PostgreSQL and Qdrant backends."""

    @abstractmethod
    async def create_document(self, document: DocumentCreate) -> DocumentResponse: ...

    @abstractmethod
    async def get_document(self, doc_id: UUID) -> DocumentResponse | None: ...

    @abstractmethod
    async def get_document_by_hash(self, sha256_hash: str) -> DocumentResponse | None: ...

    @abstractmethod
    async def delete_document(self, doc_id: UUID) -> bool: ...

    @abstractmethod
    async def insert_chunks_batch(self, chunks: list[ChunkCreate]) -> int: ...

    @abstractmethod
    async def delete_chunks_by_doc(self, doc_id: UUID) -> int: ...

    @abstractmethod
    async def search_similar_chunks(self, query_vector: list[float], query: SearchQuery) -> list[SearchResult]: ...