"""Tests for Vector API request and response schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.schemas import (
    ArtifactType,
    ChunkBatchRequest,
    ChunkBatchResponse,
    DocumentCreate,
    SearchQuery,
    SearchResponse,
    SearchResult,
)


def test_document_schema_serializes_source_metadata():
    """Document registration payloads retain JSON-safe document identity."""
    doc_id = uuid4()
    document = DocumentCreate(
        doc_id=doc_id,
        title="Quarterly report",
        source_type="pdf",
        sha256_hash="a" * 64,
        total_pages=12,
        metadata={"author": "Finance"},
    )

    payload = document.model_dump(mode="json")

    assert payload["doc_id"] == str(doc_id)
    assert payload["metadata"] == {"author": "Finance"}


def test_chunk_batch_schema_supports_optional_embeddings_and_lineage():
    """Batches retain parent-child relationships for raw and derivative chunks."""
    doc_id, parent_id, chunk_id = uuid4(), uuid4(), uuid4()
    request = ChunkBatchRequest.model_validate(
        {
            "chunks": [
                {
                    "chunk_id": str(chunk_id),
                    "doc_id": str(doc_id),
                    "parent_chunk_id": str(parent_id),
                    "artifact_type": "contextual_chunk",
                    "content": "Contextual revenue details",
                    "embedding": [0.1, 0.2],
                    "metadata": {"header_path": "# Finance"},
                }
            ]
        }
    )
    response = ChunkBatchResponse(inserted_count=1, embedded_count=0, chunk_ids=[chunk_id])

    assert request.chunks[0].artifact_type is ArtifactType.CONTEXTUAL_CHUNK
    assert request.chunks[0].parent_chunk_id == parent_id
    assert response.model_dump(mode="json")["chunk_ids"] == [str(chunk_id)]


def test_search_schema_serializes_filters_and_scored_results():
    """Search requests and results preserve filters, scores, and traceability."""
    doc_id, chunk_id = uuid4(), uuid4()
    query = SearchQuery(query="APAC revenue", artifact_types=[ArtifactType.QA_PAIR], doc_id=doc_id, score_threshold=0.7, top_k=5)
    result = SearchResult(chunk_id=chunk_id, doc_id=doc_id, artifact_type=ArtifactType.QA_PAIR, content="APAC revenue grew 14%.", score=0.92)
    response = SearchResponse(results=[result], total=1)

    assert query.model_dump(mode="json")["artifact_types"] == ["qa_pair"]
    assert response.model_dump(mode="json")["results"][0]["score"] == 0.92


@pytest.mark.parametrize(
    "model,payload",
    [
        (DocumentCreate, {"doc_id": str(uuid4()), "title": "Report", "source_type": "pdf", "sha256_hash": "bad"}),
        (ChunkBatchRequest, {"chunks": []}),
        (SearchQuery, {"query": "", "top_k": 101}),
        (SearchResult, {"chunk_id": str(uuid4()), "doc_id": str(uuid4()), "artifact_type": "raw_chunk", "content": "text", "score": 1.1}),
    ],
)
def test_schemas_reject_invalid_payloads(model, payload):
    """Boundary validation prevents malformed records from reaching storage."""
    with pytest.raises(ValidationError):
        model.model_validate(payload)