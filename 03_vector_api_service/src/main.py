"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.router import api_router
from src.config import VectorApiSettings
from src.db.factory import RepositoryFactory
from src.db.postgres.connection import PostgresPool
from src.db.qdrant.connection import QdrantConnection
from src.embeddings.factory import EmbeddingFactory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize configured storage and embedding dependencies for the API."""
    settings = VectorApiSettings()
    connection_manager = PostgresPool(settings) if settings.vector_db_backend == "postgres" else QdrantConnection(settings)
    connection = await connection_manager.connect()
    app.state.settings = settings
    app.state.connection_manager = connection_manager
    app.state.repository = RepositoryFactory.create(settings, connection)
    app.state.embedding_service = EmbeddingFactory.create(settings)
    try:
        yield
    finally:
        await connection_manager.close()


def create_app() -> FastAPI:
    """Create the versioned Vector API application."""
    app = FastAPI(title="Enterprise RAG Vector API", version="0.1.0", lifespan=lifespan)
    app.include_router(api_router)
    return app


app = create_app()