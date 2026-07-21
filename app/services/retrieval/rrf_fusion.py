from collections import defaultdict


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict]],
    k: int = 60
) -> list[dict]:
    """Fuse multiple ranked result lists using Reciprocal Rank Fusion (RRF).
    
    RRF formula: score(chunk) = sum(1 / (k + rank_i)) for each list i
    
    Args:
        ranked_lists: List of ranked result lists (each result must have 'chunk_id')
        k: Constant to smooth rank differences (default: 60)
        
    Returns:
        Fused list of results sorted by RRF score
    """
    rrf_scores: dict[int, float] = defaultdict(float)
    chunk_map: dict[int, dict] = {}
    
    for ranked_list in ranked_lists:
        for rank, chunk in enumerate(ranked_list, start=1):
            chunk_id = chunk["chunk_id"]
            rrf_scores[chunk_id] += 1.0 / (k + rank)
            
            # Store the chunk data (from first occurrence)
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk.copy()
    
    # Sort by RRF score and add the score to results
    fused_results = []
    for chunk_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
        chunk = chunk_map[chunk_id]
        chunk["score"] = round(score, 4)
        fused_results.append(chunk)
    
    return fused_results
