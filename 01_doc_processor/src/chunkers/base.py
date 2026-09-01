"""Common semantic chunker contract."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.models import Chunk


class BaseChunker(ABC):
    """Interface for converting Markdown into lineage-aware chunks."""

    @abstractmethod
    def chunk(self, markdown: str, doc_id: UUID) -> list[Chunk]:
        """Split Markdown into semantically coherent chunks for a document."""