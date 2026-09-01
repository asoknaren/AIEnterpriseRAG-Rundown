"""Tests for the Docling document parser."""

from pathlib import Path
from typing import ClassVar

import pytest

from src.parsers import DoclingParser


class FakeDocument:
    """Minimal Docling document stand-in for conversion boundary tests."""

    pages: ClassVar[dict[int, object]] = {1: object(), 2: object()}

    def export_to_markdown(self) -> str:
        return "# Revenue\n\n| Region | Growth |\n| --- | --- |\n| APAC | 14% |"


class FakeConversionResult:
    document = FakeDocument()


class FakeConverter:
    def __init__(self) -> None:
        self.sources: list[Path] = []

    def convert(self, source: Path) -> FakeConversionResult:
        self.sources.append(source)
        return FakeConversionResult()


def test_txt_parser_returns_content_and_source_metadata(tmp_path):
    """Plain text documents are normalized without invoking Docling."""
    source = tmp_path / "notes.txt"
    source.write_text("# Notes\n\nPlain text content.", encoding="utf-8")

    parsed = DoclingParser().parse(source)

    assert parsed.markdown == "# Notes\n\nPlain text content."
    assert parsed.metadata.title == "notes"
    assert parsed.metadata.source_type == "txt"
    assert parsed.metadata.total_pages == 1
    assert parsed.metadata.metadata["file_size_bytes"] == source.stat().st_size


@pytest.mark.parametrize("extension", [".pdf", ".docx", ".doc", ".html"])
def test_docling_formats_export_markdown_with_headers_and_tables(tmp_path, extension):
    """Structured formats use Docling and preserve content hierarchy."""
    source = tmp_path / f"report{extension}"
    source.write_bytes(b"fixture content")
    converter = FakeConverter()

    parsed = DoclingParser(converter_factory=lambda: converter).parse(source)

    assert converter.sources == [source]
    assert parsed.markdown.startswith("# Revenue")
    assert "| APAC | 14% |" in parsed.markdown
    assert parsed.metadata.source_type == extension.lstrip(".")
    assert parsed.metadata.total_pages == 2
    assert parsed.metadata.sha256_hash == parsed.metadata.calculate_sha256(b"fixture content")


def test_parser_rejects_missing_and_unsupported_files(tmp_path):
    """Only existing files in the supported format set may be processed."""
    parser = DoclingParser()
    unsupported = tmp_path / "record.csv"
    unsupported.write_text("region,growth", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        parser.parse(tmp_path / "missing.pdf")
    with pytest.raises(ValueError, match="Unsupported document type"):
        parser.parse(unsupported)