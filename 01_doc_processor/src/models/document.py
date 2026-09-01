"""Document-level metadata and integrity helpers."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata captured for a source document before semantic processing."""

    doc_id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1)
    source_type: str = Field(min_length=1, max_length=32)
    file_path: str | None = None
    sha256_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-fA-F0-9]{64}$")
    total_pages: int = Field(default=1, ge=1)
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def calculate_sha256(content: bytes) -> str:
        """Return the SHA-256 checksum for raw document content."""
        return sha256(content).hexdigest()

    @classmethod
    def sha256_for_file(cls, file_path: str | Path) -> str:
        """Return the SHA-256 checksum for a document file."""
        return cls.calculate_sha256(Path(file_path).read_bytes())