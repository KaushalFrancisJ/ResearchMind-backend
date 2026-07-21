import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.models.document import SessionDocument


async def keyword_search(
    db: AsyncSession,
    session_id: uuid.UUID,
    query: str,
    top_k: int = 5
) -> list[dict]:
    """Perform keyword-based search using PostgreSQL full-text search.
    
    Args:
        db: Database session
        session_id: Session ID to limit search scope
        query: Search query string
        top_k: Number of results to return
        
    Returns:
        List of chunk dictionaries with relevance scores
    """
    # Get document IDs linked to this session
    doc_ids_result = await db.execute(
        select(SessionDocument.document_id).where(SessionDocument.session_id == session_id)
    )
    doc_ids = [row[0] for row in doc_ids_result.fetchall()]

    if not doc_ids:
        return []

    # Use PostgreSQL's ts_rank for relevance scoring
    # Create a tsquery from the query string
    result = await db.execute(
        select(
            DocumentChunk.chunk_id,
            DocumentChunk.content,
            DocumentChunk.chunk_metadata,
            DocumentChunk.chunk_index,
            DocumentChunk.document_id,
            func.ts_rank(
                func.to_tsvector("english", DocumentChunk.content),
                func.plainto_tsquery("english", query)
            ).label("score"),
        )
        .where(
            DocumentChunk.document_id.in_(doc_ids),
            func.to_tsvector("english", DocumentChunk.content).op("@@")(
                func.plainto_tsquery("english", query)
            ),
        )
        .order_by(text("score DESC"))
        .limit(top_k)
    )

    return [
        {
            "chunk_id": row.chunk_id,
            "document_id": row.document_id,
            "chunk_index": row.chunk_index,
            "title": (row.chunk_metadata or {}).get("title"),
            "content": row.content,
            "score": round(row.score, 4),
        }
        for row in result.fetchall()
    ]
