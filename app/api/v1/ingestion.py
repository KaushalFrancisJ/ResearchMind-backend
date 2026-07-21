import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.repositories import chunk_repo, document_repo
from app.services.chunking import extract_chunks_from_docx, extract_chunks_from_pdf
from app.services.ingestion.metadata_extractor import extract_metadata

router = APIRouter(prefix="/ingest", tags=["ingestion"])

UPLOADS_DIR = Path(settings.UPLOADS_DIR)
UPLOADS_DIR.mkdir(exist_ok=True)


@router.post("/pdf", status_code=201)
async def ingest_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingest a PDF file: extract chunks, generate embeddings, store in database."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    contents = await file.read()
    file_hash = hashlib.sha256(contents).hexdigest()
    
    # Check if already processed
    existing = await document_repo.get_by_hash(db, file_hash)
    if existing:
        return {
            "document_id": existing.document_id,
            "status": "already_exists",
            "message": "This document was already ingested"
        }
    
    # Save file
    dest = UPLOADS_DIR / f"{file_hash}.pdf"
    dest.write_bytes(contents)
    
    # Extract metadata
    try:
        metadata = extract_metadata(dest)
        title = metadata.get("title") or file.filename
    except Exception:
        title = file.filename
    
    # Create document record
    doc = await document_repo.create_document(db, str(dest), file_hash, title)
    
    # Extract chunks and save
    chunks = list(extract_chunks_from_pdf(str(dest)))
    await chunk_repo.save_chunks(db, doc.document_id, chunks)
    
    await db.commit()
    
    return {
        "document_id": doc.document_id,
        "chunks_count": len(chunks),
        "status": "success"
    }


@router.post("/docx", status_code=201)
async def ingest_docx(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingest a DOCX file: extract chunks, generate embeddings, store in database."""
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files are accepted")
    
    contents = await file.read()
    file_hash = hashlib.sha256(contents).hexdigest()
    
    # Check if already processed
    existing = await document_repo.get_by_hash(db, file_hash)
    if existing:
        return {
            "document_id": existing.document_id,
            "status": "already_exists",
            "message": "This document was already ingested"
        }
    
    # Save file
    dest = UPLOADS_DIR / f"{file_hash}.docx"
    dest.write_bytes(contents)
    
    # Extract metadata
    try:
        metadata = extract_metadata(dest)
        title = metadata.get("title") or file.filename
    except Exception:
        title = file.filename
    
    # Create document record
    doc = await document_repo.create_document(db, str(dest), file_hash, title)
    
    # Extract chunks and save
    chunks = list(extract_chunks_from_docx(str(dest)))
    await chunk_repo.save_chunks(db, doc.document_id, chunks)
    
    await db.commit()
    
    return {
        "document_id": doc.document_id,
        "chunks_count": len(chunks),
        "status": "success"
    }
