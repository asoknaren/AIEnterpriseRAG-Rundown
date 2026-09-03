"""Vector search endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_embedding_service, get_repository
from src.db.base import BaseVectorRepository
from src.embeddings.base import BaseEmbeddingService, EmbeddingServiceError
from src.schemas import SearchQuery, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_chunks(
    query: SearchQuery,
    repository: BaseVectorRepository = Depends(get_repository),
    embedding_service: BaseEmbeddingService = Depends(get_embedding_service),
) -> SearchResponse:
    """Embed the query and return the repository's filtered similarity results."""
    try:
        query_vector = await embedding_service.embed_query(query.query)
    except EmbeddingServiceError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
    results = await repository.search_similar_chunks(query_vector, query)
    return SearchResponse(results=results, total=len(results))