"""Tests for raw asyncpg repository queries."""

from uuid import uuid4

import pytest

from src.db.postgres import PostgresVectorRepository
from src.schemas import ArtifactType, ChunkCreate, DocumentCreate, SearchQuery


class FakePool:
    def __init__(self):
        self.calls = []
        self.document = None

    async def fetchrow(self, sql, *args):
        self.calls.append((sql, args))
        if sql.startswith("INSERT"):
            self.document = {"doc_id": args[0], "title": args[1], "source_type": args[2], "file_path": args[3], "sha256_hash": args[4], "total_pages": args[5], "metadata": {}}
        return self.document

    async def execute(self, sql, *args):
        self.calls.append((sql, args))
        return "DELETE 1"

    async def executemany(self, sql, args):
        self.calls.append((sql, args))

    async def fetch(self, sql, *args):
        self.calls.append((sql, args))
        return [{"chunk_id": uuid4(), "doc_id": uuid4(), "parent_chunk_id": None, "artifact_type": "raw_chunk", "content": "APAC revenue", "raw_content": None, "metadata": {}, "score": 0.9}]


@pytest.mark.asyncio
async def test_postgres_repository_uses_parameterized_crud_batch_and_vector_sql():
    pool = FakePool()
    repository = PostgresVectorRepository(pool)
    document = DocumentCreate(doc_id=uuid4(), title="Report", source_type="pdf", sha256_hash="a" * 64)
    chunk = ChunkCreate(chunk_id=uuid4(), doc_id=document.doc_id, artifact_type=ArtifactType.RAW_CHUNK, content="APAC revenue", embedding=[0.1])

    assert (await repository.create_document(document)).doc_id == document.doc_id
    assert (await repository.get_document(document.doc_id)).title == "Report"
    assert await repository.insert_chunks_batch([chunk]) == 1
    results = await repository.search_similar_chunks([0.1], SearchQuery(query="APAC"))
    assert results[0].score == 0.9
    assert await repository.delete_document(document.doc_id)
    assert await repository.delete_chunks_by_doc(document.doc_id) == 1
    sql = "\n".join(call[0] for call in pool.calls)
    assert "embedding <=> $1" in sql
    assert "VALUES ($1" in sql