import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.retrieval.hybrid_search import hybrid_search
from app.services.retrieval.keyword_search import keyword_search
from app.services.retrieval.reranker import deduplicate_chunks, rerank_by_score
from app.services.retrieval.vector_search import vector_search


async def retrieve(
    db: AsyncSession,
    session_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    strategy: str = "hybrid",
    score_threshold: float = 0.0
) -> list[dict]:
    """Orchestrate the retrieval pipeline with configurable strategy.
    
    Args:
        db: Database session
        session_id: Session ID to limit search scope
        query: Search query string
        top_k: Number of results to return
        strategy: Retrieval strategy - "vector", "keyword", or "hybrid"
        score_threshold: Minimum relevance score (0-1)
        
    Returns:
        List of ranked and filtered chunks
    """
    # Select retrieval strategy
    if strategy == "vector":
        chunks = await vector_search(db, session_id, query, top_k * 2)
    elif strategy == "keyword":
        chunks = await keyword_search(db, session_id, query, top_k * 2)
    elif strategy == "hybrid":
        chunks = await hybrid_search(db, session_id, query, top_k * 2)
    else:
        raise ValueError(f"Unknown retrieval strategy: {strategy}")
    
    # Post-processing: deduplicate, filter, and rerank
    chunks = deduplicate_chunks(chunks)
    chunks = rerank_by_score(chunks, threshold=score_threshold)
    
    # Return top_k
    return chunks[:top_k]
