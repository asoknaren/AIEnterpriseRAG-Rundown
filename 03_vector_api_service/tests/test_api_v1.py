"""Offline API integration tests for version 1 routes."""

from types import SimpleNamespace
from uuid import UUID, uuid4

import httpx
import pytest

from src.api.dependencies import get_embedding_service, get_repository
from src.main import create_app
from src.schemas import (
    ArtifactType,
    ChunkCreate,
    DocumentCreate,
    DocumentResponse,
    SearchQuery,
    SearchResult,
)


class FakeRepository:
    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentResponse] = {}
        self.chunks: list[ChunkCreate] = []
        self.search_query: SearchQuery | None = None

    async def create_document(self, document: DocumentCreate) -> DocumentResponse:
        response = DocumentResponse.model_validate(document.model_dump())
        self.documents[document.doc_id] = response
        return response

    async def get_document(self, doc_id: UUID) -> DocumentResponse | None:
        return self.documents.get(doc_id)

    async def get_document_by_hash(self, sha256_hash: str) -> DocumentResponse | None:
        return next((item for item in self.documents.values() if item.sha256_hash == sha256_hash), None)

    async def delete_document(self, doc_id: UUID) -> bool:
        if doc_id not in self.documents:
            return False
        self.documents.pop(doc_id)
        self.chunks = [chunk for chunk in self.chunks if chunk.doc_id != doc_id]
        return True

    async def insert_chunks_batch(self, chunks: list[ChunkCreate]) -> int:
        self.chunks.extend(chunks)
        return len(chunks)

    async def search_similar_chunks(self, query_vector, query: SearchQuery) -> list[SearchResult]:
        self.search_query = query
        if not self.chunks:
            return []
        chunk = self.chunks[0]
        return [SearchResult.model_validate({**chunk.model_dump(), "score": 0.9})]


class FakeEmbeddingService:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2] for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2]


@pytest.fixture
async def client():
    app = create_app()
    app.state.settings = SimpleNamespace(vector_db_backend="postgres")
    repository = FakeRepository()
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_embedding_service] = lambda: FakeEmbeddingService()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client, repository


@pytest.mark.asyncio
async def test_document_crud_and_checksum_lookup(client):
    client, _ = client
    doc_id = uuid4()
    payload = {"doc_id": str(doc_id), "title": "Report", "source_type": "pdf", "sha256_hash": "a" * 64}

    assert (await client.post("/api/v1/documents", json=payload)).status_code == 201
    assert (await client.get(f"/api/v1/documents/{doc_id}")).status_code == 200
    assert (await client.get(f"/api/v1/documents/by-hash/{'a' * 64}")).status_code == 200
    assert (await client.post("/api/v1/documents", json=payload)).status_code == 409
    assert (await client.delete(f"/api/v1/documents/{doc_id}")).status_code == 204
    assert (await client.get(f"/api/v1/documents/{doc_id}")).status_code == 404


@pytest.mark.asyncio
async def test_chunk_batch_generates_missing_vectors_and_searches(client):
    client, repository = client
    doc_id = uuid4()
    chunk_id = uuid4()
    await client.post("/api/v1/documents", json={"doc_id": str(doc_id), "title": "Report", "source_type": "pdf", "sha256_hash": "b" * 64})

    response = await client.post("/api/v1/chunks/batch", json={"chunks": [{"chunk_id": str(chunk_id), "doc_id": str(doc_id), "artifact_type": "factoid", "content": "APAC grew 14%."}]})
    assert response.status_code == 201
    assert response.json()["embedded_count"] == 1
    assert repository.chunks[0].embedding == [0.1, 0.2]

    response = await client.post("/api/v1/search", json={"query": "How much did APAC grow?", "artifact_types": ["factoid"], "doc_id": str(doc_id)})
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert repository.search_query is not None
    assert repository.search_query.artifact_types == [ArtifactType.FACTOID]


@pytest.mark.asyncio
async def test_health_endpoint_reports_configured_backend(client):
    client, _ = client

    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "postgres"}