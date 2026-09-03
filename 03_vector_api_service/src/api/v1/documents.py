"""Document lifecycle endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_repository
from src.db.base import BaseVectorRepository
from src.schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate, repository: BaseVectorRepository = Depends(get_repository)
) -> DocumentResponse:
    """Register one source document unless its checksum already exists."""
    if await repository.get_document_by_hash(document.sha256_hash):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document checksum already exists.")
    return await repository.create_document(document)


@router.get("/by-hash/{sha256_hash}", response_model=DocumentResponse)
async def get_document_by_hash(
    sha256_hash: str, repository: BaseVectorRepository = Depends(get_repository)
) -> DocumentResponse:
    """Find a document using its source checksum."""
    document = await repository.get_document_by_hash(sha256_hash)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID, repository: BaseVectorRepository = Depends(get_repository)
) -> DocumentResponse:
    """Retrieve a document by its identifier."""
    document = await repository.get_document(doc_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: UUID, repository: BaseVectorRepository = Depends(get_repository)) -> None:
    """Delete a document and its backend-managed child chunks."""
    if not await repository.delete_document(doc_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")