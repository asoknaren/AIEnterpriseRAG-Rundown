"""Vector similarity search request and response schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from .chunk_dto import ArtifactType


class SearchQuery(BaseModel):
    """A text query with optional lineage and artifact filters."""

    query: str = Field(min_length=1)
    artifact_types: list[ArtifactType] | None = None
    doc_id: UUID | None = None
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    top_k: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    """One scored chunk returned from a vector similarity search."""

    chunk_id: UUID
    doc_id: UUID
    parent_chunk_id: UUID | None = None
    artifact_type: ArtifactType
    content: str
    raw_content: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    score: float = Field(ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Ordered vector search results and their requested count."""

    results: list[SearchResult] = Field(default_factory=list)
    total: int = Field(ge=0)