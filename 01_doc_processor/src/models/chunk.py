"""Semantic chunk and derivative artifact models."""

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Representations emitted by the document processing pipeline."""

    RAW_CHUNK = "raw_chunk"
    CONTEXTUAL_CHUNK = "contextual_chunk"
    RAPTOR_SUMMARY = "raptor_summary"
    QA_PAIR = "qa_pair"
    FACTOID = "factoid"
    SUMMARY = "summary"


class Chunk(BaseModel):
    """A chunk of source content or an LLM-derived artifact."""

    chunk_id: UUID = Field(default_factory=uuid4)
    doc_id: UUID
    parent_chunk_id: UUID | None = None
    artifact_type: ArtifactType = ArtifactType.RAW_CHUNK
    content: str = Field(min_length=1)
    raw_content: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)