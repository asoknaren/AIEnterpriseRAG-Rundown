"""Chunk ingestion endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_embedding_service, get_repository
from src.db.base import BaseVectorRepository
from src.embeddings.base import BaseEmbeddingService, EmbeddingServiceError
from src.schemas import ChunkBatchRequest, ChunkBatchResponse

router = APIRouter(prefix="/chunks", tags=["chunks"])


@router.post("/batch", response_model=ChunkBatchResponse, status_code=status.HTTP_201_CREATED)
async def insert_chunks_batch(
    request: ChunkBatchRequest,
    repository: BaseVectorRepository = Depends(get_repository),
    embedding_service: BaseEmbeddingService = Depends(get_embedding_service),
) -> ChunkBatchResponse:
    """Store chunks and generate vectors only for chunks that do not provide one."""
    missing_vectors = [chunk for chunk in request.chunks if chunk.embedding is None]
    if missing_vectors:
        try:
            vectors = await embedding_service.embed_texts([chunk.content for chunk in missing_vectors])
        except EmbeddingServiceError as error:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
        vectors_by_id = {chunk.chunk_id: vector for chunk, vector in zip(missing_vectors, vectors, strict=True)}
        chunks = [chunk.model_copy(update={"embedding": vectors_by_id[chunk.chunk_id]}) if chunk.embedding is None else chunk for chunk in request.chunks]
    else:
        chunks = request.chunks
    inserted_count = await repository.insert_chunks_batch(chunks)
    return ChunkBatchResponse(
        inserted_count=inserted_count,
        embedded_count=len(missing_vectors),
        chunk_ids=[chunk.chunk_id for chunk in chunks],
    )