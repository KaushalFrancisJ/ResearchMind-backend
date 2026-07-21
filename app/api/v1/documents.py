import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories import document_repo
from app.schemas.document import SessionDocumentItem

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=SessionDocumentItem)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific document by ID."""
    doc = await document_repo.get_by_id(db, document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return SessionDocumentItem.model_validate(doc)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and all its chunks.
    
    This will cascade delete all associated chunks and session links.
    """
    deleted = await document_repo.delete_document(db, document_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.commit()
