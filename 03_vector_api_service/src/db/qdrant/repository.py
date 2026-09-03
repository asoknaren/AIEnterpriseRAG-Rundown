"""Async Qdrant vector storage implementation."""

from typing import Any
from uuid import UUID

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
)

from src.db.base import BaseVectorRepository
from src.schemas import (
    ChunkCreate,
    DocumentCreate,
    DocumentResponse,
    SearchQuery,
    SearchResult,
)


class QdrantVectorRepository(BaseVectorRepository):
    """Qdrant implementation storing documents and chunks as payloads."""

    def __init__(self, client: Any, collection_name: str) -> None:
        self._client = client
        self._collection_name = collection_name
        self._documents: dict[UUID, DocumentResponse] = {}

    async def create_document(self, document: DocumentCreate) -> DocumentResponse:
        response = DocumentResponse.model_validate(document.model_dump())
        self._documents[document.doc_id] = response
        return response

    async def get_document(self, doc_id: UUID) -> DocumentResponse | None:
        return self._documents.get(doc_id)

    async def get_document_by_hash(self, sha256_hash: str) -> DocumentResponse | None:
        return next((document for document in self._documents.values() if document.sha256_hash == sha256_hash), None)

    async def delete_document(self, doc_id: UUID) -> bool:
        existed = doc_id in self._documents
        self._documents.pop(doc_id, None)
        await self.delete_chunks_by_doc(doc_id)
        return existed

    async def insert_chunks_batch(self, chunks: list[ChunkCreate]) -> int:
        points = [PointStruct(id=str(chunk.chunk_id), vector=chunk.embedding or [], payload=chunk.model_dump(mode="json", exclude={"embedding"})) for chunk in chunks]
        if points:
            await self._client.upsert(collection_name=self._collection_name, points=points)
        return len(points)

    async def delete_chunks_by_doc(self, doc_id: UUID) -> int:
        from qdrant_client.models import FilterSelector

        result = await self._client.delete(collection_name=self._collection_name, points_selector=FilterSelector(filter=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=str(doc_id)))])))
        return 0 if result is None else 1

    async def search_similar_chunks(self, query_vector: list[float], query: SearchQuery) -> list[SearchResult]:
        conditions: list[Any] = []
        if query.doc_id:
            conditions.append(FieldCondition(key="doc_id", match=MatchValue(value=str(query.doc_id))))
        if query.artifact_types:
            conditions.append(FieldCondition(key="artifact_type", match=MatchAny(any=[item.value for item in query.artifact_types])))
        response = await self._client.query_points(
            collection_name=self._collection_name, query=query_vector, query_filter=Filter(must=conditions) if conditions else None,
            limit=query.top_k, score_threshold=query.score_threshold, with_payload=True,
        )
        return [SearchResult.model_validate({**point.payload, "score": point.score}) for point in response.points]