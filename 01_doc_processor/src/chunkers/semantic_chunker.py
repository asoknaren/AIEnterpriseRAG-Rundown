"""Chonkie-backed semantic chunking with Markdown lineage metadata."""

from collections.abc import Callable
from re import MULTILINE, finditer
from typing import Any
from uuid import UUID

from src.config import ProcessorSettings, settings
from src.models import Chunk

from .base import BaseChunker


class SemanticChunker(BaseChunker):
    """Build raw chunks with source offsets and heading breadcrumbs."""

    def __init__(
        self,
        processor_settings: ProcessorSettings = settings,
        chunker_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._settings = processor_settings
        factory = chunker_factory or self._create_chunker
        self._chunker = factory(
            threshold=processor_settings.similarity_threshold,
            chunk_size=processor_settings.chunk_size,
        )

    @staticmethod
    def _create_chunker(**kwargs: Any) -> Any:
        from chonkie import SemanticChunker as ChonkieSemanticChunker

        return ChonkieSemanticChunker(**kwargs)

    def chunk(self, markdown: str, doc_id: UUID) -> list[Chunk]:
        """Split Markdown and retain source-character and token offsets."""
        if not markdown.strip():
            return []

        token_offset = 0
        chunks: list[Chunk] = []
        for source_chunk in self._chunker.chunk(markdown):
            token_end = token_offset + source_chunk.token_count
            chunks.append(
                Chunk(
                    doc_id=doc_id,
                    content=source_chunk.text,
                    raw_content=source_chunk.text,
                    metadata={
                        "header_path": self._header_path(markdown, source_chunk.start_index),
                        "char_start": source_chunk.start_index,
                        "char_end": source_chunk.end_index,
                        "token_start": token_offset,
                        "token_end": token_end,
                    },
                )
            )
            token_offset = token_end
        return chunks

    @staticmethod
    def _header_path(markdown: str, position: int) -> str:
        headings: list[str | None] = [None] * 6
        for match in finditer(r"^(#{1,6})\s+(.+?)\s*$", markdown, MULTILINE):
            if match.start() > position:
                break
            level = len(match.group(1))
            headings[level - 1] = f"{match.group(1)} {match.group(2)}"
            for index in range(level, len(headings)):
                headings[index] = None
        return " > ".join(heading for heading in headings if heading is not None)