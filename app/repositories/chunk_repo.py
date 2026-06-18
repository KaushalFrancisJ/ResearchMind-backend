import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.services.chunking.chunk_models import Chunk
from app.services.embeddings.embedding_service import embed


async def save_chunks(db: AsyncSession, document_id: uuid.UUID, chunks: list[Chunk]) -> int:
    texts = [f"{c.title}\n\n{c.content}" for c in chunks]
    vectors = embed(texts)

    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        db.add(DocumentChunk(
            document_id=document_id,
            content=chunk.content,
            chunk_index=i,
            chunk_metadata={"id": chunk.id, "module": chunk.module, "title": chunk.title},
            embedding=vector,
        ))

    await db.flush()
    return len(chunks)
