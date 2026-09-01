"""Tests for semantic chunking and Markdown lineage metadata."""

from dataclasses import dataclass
from uuid import uuid4

from src.chunkers import SemanticChunker
from src.config import ProcessorSettings


@dataclass
class FakeChonkieChunk:
    text: str
    start_index: int
    end_index: int
    token_count: int


class FakeChonkieChunker:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.inputs: list[str] = []

    def chunk(self, markdown: str) -> list[FakeChonkieChunk]:
        self.inputs.append(markdown)
        intro_start = markdown.index("Introduction")
        results_start = markdown.index("Revenue")
        return [
            FakeChonkieChunk("Introduction text.", intro_start, intro_start + 18, 3),
            FakeChonkieChunk("Revenue increased.", results_start, results_start + 18, 4),
        ]


def test_semantic_chunker_preserves_boundaries_offsets_and_header_lineage():
    """Chonkie output is enriched with traceable source and heading metadata."""
    markdown = "# Report\n\nIntroduction text.\n\n## Results\n\nRevenue increased."
    fake_chunker = FakeChonkieChunker()
    factory_kwargs: dict[str, float | int] = {}

    def create_chunker(**kwargs):
        factory_kwargs.update(kwargs)
        return fake_chunker

    settings = ProcessorSettings(chunk_size=64, similarity_threshold=0.6)
    chunker = SemanticChunker(settings, chunker_factory=create_chunker)

    chunks = chunker.chunk(markdown, uuid4())

    assert factory_kwargs == {"threshold": 0.6, "chunk_size": 64}
    assert fake_chunker.inputs == [markdown]
    assert [chunk.content for chunk in chunks] == ["Introduction text.", "Revenue increased."]
    assert chunks[0].metadata == {
        "header_path": "# Report",
        "char_start": markdown.index("Introduction"),
        "char_end": markdown.index("Introduction") + 18,
        "token_start": 0,
        "token_end": 3,
    }
    assert chunks[1].metadata == {
        "header_path": "# Report > ## Results",
        "char_start": markdown.index("Revenue"),
        "char_end": markdown.index("Revenue") + 18,
        "token_start": 3,
        "token_end": 7,
    }


def test_semantic_chunker_returns_no_chunks_for_blank_markdown():
    """Blank documents do not invoke semantic chunking."""
    fake_chunker = FakeChonkieChunker()
    chunker = SemanticChunker(chunker_factory=lambda **kwargs: fake_chunker)

    assert chunker.chunk(" \n", uuid4()) == []
    assert fake_chunker.inputs == []