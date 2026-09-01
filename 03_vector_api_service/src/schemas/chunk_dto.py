"""Chunk batch ingestion request and response schemas."""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Stored source and derivative artifact representations."""

    RAW_CHUNK = "raw_chunk"
    CONTEXTUAL_CHUNK = "contextual_chunk"
    RAPTOR_SUMMARY = "raptor_summary"
    QA_PAIR = "qa_pair"
    FACTOID = "factoid"
    SUMMARY = "summary"


class ChunkCreate(BaseModel):
    """One lineage-aware chunk record accepted for vector storage."""

    chunk_id: UUID
    doc_id: UUID
    parent_chunk_id: UUID | None = None
    artifact_type: ArtifactType
    content: str = Field(min_length=1)
    raw_content: str | None = None
    embedding: list[float] | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class ChunkBatchRequest(BaseModel):
    """Bounded batch of chunks sent to the ingestion endpoint."""

    chunks: list[ChunkCreate] = Field(min_length=1, max_length=500)


class ChunkBatchResponse(BaseModel):
    """Summary of accepted and embedding-generated chunk records."""

    inserted_count: int = Field(ge=0)
    embedded_count: int = Field(ge=0)
    chunk_ids: list[UUID] = Field(default_factory=list)