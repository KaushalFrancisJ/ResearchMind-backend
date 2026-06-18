import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.models.document import SessionDocument
from app.services.embeddings.embedding_service import embed


async def vector_search(db: AsyncSession, session_id: uuid.UUID, query: str, top_k: int = 5) -> list[dict]:
    query_vector = embed([query])[0]

    # Get document_ids linked to this session
    doc_ids_result = await db.execute(
        select(SessionDocument.document_id).where(SessionDocument.session_id == session_id)
    )
    doc_ids = [row[0] for row in doc_ids_result.fetchall()]

    if not doc_ids:
        return []

    result = await db.execute(
        select(
            DocumentChunk.chunk_id,
            DocumentChunk.content,
            DocumentChunk.chunk_metadata,
            DocumentChunk.chunk_index,
            DocumentChunk.document_id,
            (1 - DocumentChunk.embedding.cosine_distance(query_vector)).label("score"),
        )
        .where(DocumentChunk.document_id.in_(doc_ids))
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
