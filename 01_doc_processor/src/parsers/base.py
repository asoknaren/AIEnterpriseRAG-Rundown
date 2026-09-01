"""Common document parser contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from src.models import DocumentMetadata


@dataclass(frozen=True)
class ParsedDocument:
    """Normalized Markdown and metadata produced from a source document."""

    markdown: str
    metadata: DocumentMetadata


class BaseParser(ABC):
    """Interface for converting a source file into normalized Markdown."""

    @abstractmethod
    def parse(self, source_path: str | Path) -> ParsedDocument:
        """Parse a source document and return its normalized representation."""