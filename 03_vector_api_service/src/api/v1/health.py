"""Service health endpoint."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    """Report that the API completed initialization and identify its backend."""
    return {"status": "healthy", "database": request.app.state.settings.vector_db_backend}