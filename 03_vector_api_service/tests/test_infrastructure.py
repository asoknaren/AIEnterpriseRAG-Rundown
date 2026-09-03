"""Tests for storage connection lifecycles and backend initialization helpers."""

import sys
from types import ModuleType

import pytest

from src.config import VectorApiSettings
from src.db.factory import RepositoryFactory
from src.db.postgres import PostgresVectorRepository
from src.db.postgres.connection import PostgresPool
from src.db.qdrant import QdrantConnection, QdrantVectorRepository
from src.db.qdrant.schema import ensure_collection


class FakePostgresPool:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeQdrantClient:
    def __init__(self, exists: bool = False) -> None:
        self.exists = exists
        self.closed = False
        self.created = []

    async def collection_exists(self, collection_name: str) -> bool:
        return self.exists

    async def create_collection(self, **kwargs) -> None:
        self.created.append(kwargs)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_postgres_pool_creates_once_and_closes(monkeypatch):
    created = []
    fake_pool = FakePostgresPool()

    async def create_pool(**kwargs):
        created.append(kwargs)
        return fake_pool

    fake_asyncpg = ModuleType("asyncpg")
    fake_asyncpg.create_pool = create_pool
    monkeypatch.setitem(sys.modules, "asyncpg", fake_asyncpg)
    manager = PostgresPool(VectorApiSettings())

    assert await manager.connect() is fake_pool
    assert await manager.connect() is fake_pool
    assert created[0]["dsn"].endswith("/ragdb")
    await manager.close()
    assert fake_pool.closed
    assert manager.pool is None


@pytest.mark.asyncio
async def test_qdrant_connection_creates_once_and_closes(monkeypatch):
    created = []

    class FakeAsyncQdrantClient(FakeQdrantClient):
        def __init__(self, **kwargs) -> None:
            super().__init__()
            created.append(kwargs)

    import qdrant_client

    monkeypatch.setattr(qdrant_client, "AsyncQdrantClient", FakeAsyncQdrantClient)
    manager = QdrantConnection(VectorApiSettings(vector_db_backend="qdrant"))

    client = await manager.connect()
    assert await manager.connect() is client
    assert created == [{"url": "http://localhost:6333", "api_key": None}]
    await manager.close()
    assert client.closed
    assert manager.client is None


@pytest.mark.asyncio
async def test_qdrant_collection_is_created_only_when_missing():
    settings = VectorApiSettings()
    missing_client = FakeQdrantClient(exists=False)
    existing_client = FakeQdrantClient(exists=True)

    await ensure_collection(missing_client, settings)
    await ensure_collection(existing_client, settings)

    assert missing_client.created[0]["collection_name"] == settings.qdrant_collection_name
    assert missing_client.created[0]["vectors_config"].size == 1536
    assert existing_client.created == []


def test_repository_factory_selects_the_configured_backend():
    assert isinstance(RepositoryFactory.create(VectorApiSettings(), object()), PostgresVectorRepository)
    assert isinstance(
        RepositoryFactory.create(VectorApiSettings(vector_db_backend="qdrant"), object()),
        QdrantVectorRepository,
    )