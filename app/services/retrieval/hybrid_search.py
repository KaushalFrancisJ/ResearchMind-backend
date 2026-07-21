import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.retrieval.keyword_search import keyword_search
from app.services.retrieval.rrf_fusion import reciprocal_rank_fusion
from app.services.retrieval.vector_search import vector_search


async def hybrid_search(
    db: AsyncSession,
    session_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    vector_weight: float = 0.5
) -> list[dict]:
    """Perform hybrid search combining vector and keyword search.
    
    Args:
        db: Database session
        session_id: Session ID to limit search scope
        query: Search query string
        top_k: Number of final results to return
        vector_weight: Weight for vector search (0-1), keyword gets (1-weight)
        
    Returns:
        List of fused chunk results with relevance scores
    """
    # Retrieve more results from each method to have better fusion
    retrieve_k = top_k * 2
    
    # Run both searches in parallel
    vector_results = await vector_search(db, session_id, query, retrieve_k)
    keyword_results = await keyword_search(db, session_id, query, retrieve_k)
    
    # Use RRF to fuse the results
    fused_results = reciprocal_rank_fusion([vector_results, keyword_results])
    
    # Return top_k results
    return fused_results[:top_k]
