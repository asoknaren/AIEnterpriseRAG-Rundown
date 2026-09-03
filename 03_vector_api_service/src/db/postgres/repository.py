"""Raw parameterized asyncpg queries for pgvector storage."""

import json
from typing import Any
from uuid import UUID

from src.db.base import BaseVectorRepository
from src.schemas import (
    ChunkCreate,
    DocumentCreate,
    DocumentResponse,
    SearchQuery,
    SearchResult,
)


class PostgresVectorRepository(BaseVectorRepository):
    """PostgreSQL implementation using asyncpg directly without an ORM."""

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def create_document(self, document: DocumentCreate) -> DocumentResponse:
        row = await self._pool.fetchrow(
            """INSERT INTO documents (doc_id, title, source_type, file_path, sha256_hash, total_pages, doc_metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
            RETURNING doc_id, title, source_type, file_path, sha256_hash, total_pages, doc_metadata AS metadata, created_at, updated_at""",
            document.doc_id, document.title, document.source_type, document.file_path, document.sha256_hash,
            document.total_pages, json.dumps(document.metadata),
        )
        return DocumentResponse.model_validate(dict(row))

    async def get_document(self, doc_id: UUID) -> DocumentResponse | None:
        return await self._get_document("doc_id", doc_id)

    async def get_document_by_hash(self, sha256_hash: str) -> DocumentResponse | None:
        return await self._get_document("sha256_hash", sha256_hash)

    async def _get_document(self, field: str, value: UUID | str) -> DocumentResponse | None:
        row = await self._pool.fetchrow(
            f"SELECT doc_id, title, source_type, file_path, sha256_hash, total_pages, doc_metadata AS metadata, created_at, updated_at FROM documents WHERE {field} = $1",
            value,
        )
        return DocumentResponse.model_validate(dict(row)) if row else None

    async def delete_document(self, doc_id: UUID) -> bool:
        result = await self._pool.execute("DELETE FROM documents WHERE doc_id = $1", doc_id)
        return result.endswith("1")

    async def insert_chunks_batch(self, chunks: list[ChunkCreate]) -> int:
        if not chunks:
            return 0
        await self._pool.executemany(
            """INSERT INTO document_chunks (chunk_id, doc_id, parent_chunk_id, artifact_type, content, raw_content, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)""",
            [(chunk.chunk_id, chunk.doc_id, chunk.parent_chunk_id, chunk.artifact_type.value, chunk.content, chunk.raw_content, chunk.embedding, json.dumps(chunk.metadata)) for chunk in chunks],
        )
        return len(chunks)

    async def delete_chunks_by_doc(self, doc_id: UUID) -> int:
        result = await self._pool.execute("DELETE FROM document_chunks WHERE doc_id = $1", doc_id)
        return int(result.rsplit(" ", maxsplit=1)[-1])

    async def search_similar_chunks(self, query_vector: list[float], query: SearchQuery) -> list[SearchResult]:
        rows = await self._pool.fetch(
            """SELECT chunk_id, doc_id, parent_chunk_id, artifact_type, content, raw_content, metadata,
            1 - (embedding <=> $1) AS score FROM document_chunks
            WHERE ($2::uuid IS NULL OR doc_id = $2) AND ($3::text[] IS NULL OR artifact_type = ANY($3))
            AND 1 - (embedding <=> $1) >= $4 ORDER BY embedding <=> $1 LIMIT $5""",
            query_vector, query.doc_id, [item.value for item in query.artifact_types] if query.artifact_types else None,
            query.score_threshold, query.top_k,
        )
        return [SearchResult.model_validate(dict(row)) for row in rows]