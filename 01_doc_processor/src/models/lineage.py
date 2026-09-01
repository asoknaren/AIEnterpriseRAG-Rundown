"""Unified artifact lineage envelope."""

from uuid import UUID

from pydantic import BaseModel, Field

from .chunk import ArtifactType


class LineageEnvelope(BaseModel):
    """Transport-ready record that preserves document and chunk provenance."""

    doc_id: UUID
    doc_title: str = Field(min_length=1)
    doc_sha256: str = Field(min_length=64, max_length=64, pattern=r"^[a-fA-F0-9]{64}$")
    doc_source_type: str = Field(min_length=1, max_length=32)
    chunk_id: UUID
    parent_chunk_id: UUID | None = None
    artifact_type: ArtifactType
    content: str = Field(min_length=1)
    raw_content: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)