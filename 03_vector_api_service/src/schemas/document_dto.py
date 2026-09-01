"""Document registration request and response schemas."""

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Source document metadata accepted by the registration endpoint."""

    doc_id: UUID
    title: str = Field(min_length=1)
    source_type: str = Field(min_length=1, max_length=32)
    file_path: str | None = None
    sha256_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-fA-F0-9]{64}$")
    total_pages: int = Field(default=1, ge=1)
    metadata: dict[str, object] = Field(default_factory=dict)


class DocumentResponse(DocumentCreate):
    """Persisted document metadata returned by the API."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))