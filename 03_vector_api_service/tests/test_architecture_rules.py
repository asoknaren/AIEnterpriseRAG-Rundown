"""Architecture constraints for the Vector API service."""

from pathlib import Path


def test_source_never_imports_or_declares_sqlalchemy():
    """The service must use asyncpg directly and never introduce SQLAlchemy."""
    source_root = Path(__file__).parents[1] / "src"
    matches = [path for path in source_root.rglob("*.py") if "sqlalchemy" in path.read_text(encoding="utf-8").lower()]
    assert matches == []