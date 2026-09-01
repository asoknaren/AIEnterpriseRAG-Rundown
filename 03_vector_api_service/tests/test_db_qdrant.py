"""Tests for Qdrant repository operations and vector filters."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.db.qdrant import QdrantVectorRepository
from src.schemas import ArtifactType, ChunkCreate, DocumentCreate, SearchQuery


class FakeQdrantClient:
    def __init__(self):
        self.upserts = []
        self.deletes = []
        self.queries = []

    async def upsert(self, **kwargs):
        self.upserts.append(kwargs)

    async def delete(self, **kwargs):
        self.deletes.append(kwargs)
        return object()

    async def query_points(self, **kwargs):
        self.queries.append(kwargs)
        return SimpleNamespace(points=[SimpleNamespace(payload={"chunk_id": str(uuid4()), "doc_id": str(uuid4()), "parent_chunk_id": None, "artifact_type": "factoid", "content": "APAC grew 14%.", "raw_content": None, "metadata": {}}, score=0.88)])


@pytest.mark.asyncio
async def test_qdrant_repository_stores_payloads_and_applies_vector_filters():
    client = FakeQdrantClient()
    repository = QdrantVectorRepository(client, "artifacts")
    document = DocumentCreate(doc_id=uuid4(), title="Report", source_type="pdf", sha256_hash="a" * 64)
    chunk = ChunkCreate(chunk_id=uuid4(), doc_id=document.doc_id, artifact_type=ArtifactType.FACTOID, content="APAC grew 14%.", embedding=[0.1])

    assert (await repository.create_document(document)).doc_id == document.doc_id
    assert (await repository.get_document_by_hash("a" * 64)).doc_id == document.doc_id
    assert await repository.insert_chunks_batch([chunk]) == 1
    results = await repository.search_similar_chunks([0.1], SearchQuery(query="APAC", doc_id=document.doc_id, artifact_types=[ArtifactType.FACTOID]))
    assert results[0].artifact_type is ArtifactType.FACTOID
    assert client.upserts[0]["collection_name"] == "artifacts"
    assert client.queries[0]["query_filter"] is not None
    assert await repository.delete_document(document.doc_id)
    assert client.deletes