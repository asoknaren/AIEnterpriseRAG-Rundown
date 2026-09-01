"""Tests for document, chunk, and lineage models."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.models import ArtifactType, Chunk, DocumentMetadata, LineageEnvelope


def test_document_metadata_serializes_and_calculates_sha256():
    """Document metadata keeps a JSON-safe identifier and checksum."""
    checksum = DocumentMetadata.calculate_sha256(b"enterprise rag")
    document = DocumentMetadata(
        title="Architecture",
        source_type="pdf",
        sha256_hash=checksum,
        total_pages=4,
    )

    payload = document.model_dump(mode="json")
    assert payload["doc_id"] == str(document.doc_id)
    assert payload["sha256_hash"] == checksum
    assert len(checksum) == 64


def test_chunk_and_envelope_preserve_parent_child_uuid_lineage():
    """Artifacts retain UUID lineage when serialized for ingestion."""
    doc_id = uuid4()
    parent_chunk = Chunk(doc_id=doc_id, content="Parent summary")
    child_chunk = Chunk(doc_id=doc_id, parent_chunk_id=parent_chunk.chunk_id, content="Leaf text")
    envelope = LineageEnvelope(
        doc_id=doc_id,
        doc_title="Architecture",
        doc_sha256="a" * 64,
        doc_source_type="pdf",
        chunk_id=child_chunk.chunk_id,
        parent_chunk_id=child_chunk.parent_chunk_id,
        artifact_type=ArtifactType.CONTEXTUAL_CHUNK,
        content="Contextual leaf text",
        raw_content=child_chunk.content,
    )

    payload = envelope.model_dump(mode="json")
    assert payload["doc_id"] == str(doc_id)
    assert payload["chunk_id"] == str(child_chunk.chunk_id)
    assert payload["parent_chunk_id"] == str(parent_chunk.chunk_id)
    assert payload["artifact_type"] == "contextual_chunk"


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (DocumentMetadata, {"title": "Invalid", "source_type": "txt", "sha256_hash": "bad"}),
        (Chunk, {"doc_id": "not-a-uuid", "content": "Text"}),
        (
            LineageEnvelope,
            {
                "doc_id": str(uuid4()),
                "doc_title": "Invalid",
                "doc_sha256": "a" * 64,
                "doc_source_type": "txt",
                "chunk_id": str(uuid4()),
                "parent_chunk_id": "not-a-uuid",
                "artifact_type": "raw_chunk",
                "content": "Text",
            },
        ),
    ],
)
def test_models_reject_invalid_hashes_and_lineage_identifiers(model, payload):
    """Checksums and lineage identifiers must be valid before ingestion."""
    with pytest.raises(ValidationError):
        model.model_validate(payload)