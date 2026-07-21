def rerank_by_score(chunks: list[dict], threshold: float = 0.0) -> list[dict]:
    """Simple reranker that filters by score threshold and sorts.
    
    Args:
        chunks: List of chunk dictionaries with 'score' field
        threshold: Minimum score threshold (0-1)
        
    Returns:
        Filtered and sorted list of chunks
    """
    filtered = [c for c in chunks if c.get("score", 0) >= threshold]
    return sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)


def rerank_by_position(chunks: list[dict]) -> list[dict]:
    """Rerank chunks by their position in the document (earlier is better).
    
    Useful for giving preference to introductory sections.
    
    Args:
        chunks: List of chunk dictionaries with 'chunk_index' field
        
    Returns:
        Chunks sorted by position, preserving original score as secondary sort
    """
    return sorted(
        chunks,
        key=lambda x: (x.get("chunk_index", float("inf")), -x.get("score", 0))
    )


def deduplicate_chunks(chunks: list[dict]) -> list[dict]:
    """Remove duplicate chunks based on chunk_id, keeping highest score.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Deduplicated list of chunks
    """
    seen = {}
    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        if chunk_id not in seen or chunk.get("score", 0) > seen[chunk_id].get("score", 0):
            seen[chunk_id] = chunk
    
    return list(seen.values())
