"""Tests for configurable embedding providers and factory selection."""

from types import SimpleNamespace

import pytest

from src.config import VectorApiSettings
from src.embeddings import EmbeddingFactory, EmbeddingServiceError
from src.embeddings.fastembed_embed import FastEmbedService
from src.embeddings.ollama_embed import OllamaEmbeddingService
from src.embeddings.openai_embed import OpenAIEmbeddingService


class FakeOllamaClient:
    def __init__(self) -> None:
        self.calls = []

    async def embed(self, **kwargs):
        self.calls.append(kwargs)
        return {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}


class FakeFastEmbedClient:
    def __init__(self) -> None:
        self.calls = []

    def embed(self, texts):
        self.calls.append(texts)
        return iter([[0.1, 0.2] for _ in texts])


class FakeOpenAIEmbeddings:
    def __init__(self) -> None:
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])])


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.embeddings = FakeOpenAIEmbeddings()


@pytest.mark.asyncio
async def test_ollama_service_embeds_batches_and_queries():
    client = FakeOllamaClient()
    service = OllamaEmbeddingService("nomic-embed-text", 2, "http://ollama", client)

    assert await service.embed_texts(["first", "second"]) == [[0.1, 0.2], [0.3, 0.4]]
    assert client.calls == [{"model": "nomic-embed-text", "input": ["first", "second"]}]


@pytest.mark.asyncio
async def test_fastembed_service_embeds_batches():
    client = FakeFastEmbedClient()
    service = FastEmbedService("BAAI/bge-small-en-v1.5", 2, client)

    assert await service.embed_texts(["first", "second"]) == [[0.1, 0.2], [0.1, 0.2]]
    assert client.calls == [["first", "second"]]


@pytest.mark.asyncio
async def test_openai_service_embeds_queries():
    client = FakeOpenAIClient()
    service = OpenAIEmbeddingService("text-embedding-3-small", 2, "key", client)

    assert await service.embed_query("question") == [0.1, 0.2]
    assert client.embeddings.calls == [{"model": "text-embedding-3-small", "input": ["question"]}]


@pytest.mark.asyncio
async def test_embedding_service_rejects_invalid_vector_dimensions():
    service = FastEmbedService("test-model", 3, FakeFastEmbedClient())

    with pytest.raises(EmbeddingServiceError, match="Expected embedding dimension 3"):
        await service.embed_texts(["first"])


def test_factory_selects_configured_provider():
    assert isinstance(
        EmbeddingFactory.create(
            VectorApiSettings(embedding_provider="ollama", embedding_model="nomic-embed-text"), FakeOllamaClient()
        ),
        OllamaEmbeddingService,
    )
    assert isinstance(
        EmbeddingFactory.create(
            VectorApiSettings(
                embedding_provider="fastembed", embedding_model="BAAI/bge-small-en-v1.5"
            ),
            FakeFastEmbedClient(),
        ),
        FastEmbedService,
    )
    assert isinstance(
        EmbeddingFactory.create(
            VectorApiSettings(
                embedding_provider="openai", embedding_model="text-embedding-3-small"
            ),
            FakeOpenAIClient(),
        ),
        OpenAIEmbeddingService,
    )


def test_factory_requires_openai_key_when_creating_a_real_client():
    settings = VectorApiSettings(embedding_provider="openai", openai_api_key=None)

    with pytest.raises(ValueError, match="openai_api_key is required"):
        EmbeddingFactory.create(settings)