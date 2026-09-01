"""Docling adapter for structured document conversion."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

from src.models import DocumentMetadata

from .base import BaseParser, ParsedDocument


class DoclingParser(BaseParser):
    """Convert supported documents to Markdown while retaining source metadata."""

    _DOCLING_EXTENSIONS: ClassVar[set[str]] = {".pdf", ".doc", ".docx", ".html", ".htm"}
    _TEXT_EXTENSIONS: ClassVar[set[str]] = {".txt"}

    def __init__(self, converter_factory: Callable[[], Any] | None = None) -> None:
        self._converter_factory = converter_factory or self._create_converter

    @staticmethod
    def _create_converter() -> Any:
        from docling.document_converter import DocumentConverter

        return DocumentConverter()

    def parse(self, source_path: str | Path) -> ParsedDocument:
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Document does not exist: {path}")

        extension = path.suffix.lower()
        if extension in self._TEXT_EXTENSIONS:
            markdown = path.read_text(encoding="utf-8")
            page_count = 1
        elif extension in self._DOCLING_EXTENSIONS:
            result = self._converter_factory().convert(path)
            markdown = result.document.export_to_markdown()
            page_count = max(1, len(getattr(result.document, "pages", {})))
        else:
            raise ValueError(f"Unsupported document type: {extension or '<none>'}")

        return ParsedDocument(
            markdown=markdown.strip(),
            metadata=DocumentMetadata(
                title=path.stem,
                source_type=extension.lstrip("."),
                file_path=str(path),
                sha256_hash=DocumentMetadata.sha256_for_file(path),
                total_pages=page_count,
                metadata={"file_size_bytes": path.stat().st_size},
            ),
        )