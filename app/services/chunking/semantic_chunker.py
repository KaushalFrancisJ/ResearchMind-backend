from typing import Generator

import numpy as np

from app.services.chunking.chunk_models import Chunk, slugify
from app.services.embeddings.embedding_service import embed


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two 1-D vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def semantic_chunking(
    text: str,
    module_name: str,
    similarity_threshold: float = 0.75,
    min_chunk_size: int = 100,
    max_chunk_size: int = 1000
) -> Generator[Chunk, None, None]:
    """Split text into semantically coherent chunks using embedding similarity.
    
    Args:
        text: Full document text to chunk
        module_name: Document/module identifier
        similarity_threshold: Cosine similarity threshold for grouping sentences (0-1)
        min_chunk_size: Minimum chunk length in characters
        max_chunk_size: Maximum chunk length in characters
        
    Yields:
        Chunk objects with semantic boundaries
    """
    # Split into sentences (simple approach)
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    
    if not sentences:
        return
    
    # Generate embeddings for all sentences
    embeddings = np.array(embed(sentences))
    
    # Group sentences based on semantic similarity
    current_chunk: list[str] = [sentences[0]]
    current_embedding = embeddings[0].reshape(1, -1)
    chunk_index = 0
    
    for i in range(1, len(sentences)):
        sentence = sentences[i]
        sentence_embedding = embeddings[i].reshape(1, -1)
        
        # Calculate similarity with current chunk
        similarity = _cosine_similarity(current_embedding[0], sentence_embedding[0])
        
        # Estimate chunk size
        chunk_text = " ".join(current_chunk)
        
        # Decide whether to extend current chunk or start new one
        if (similarity >= similarity_threshold and 
            len(chunk_text) < max_chunk_size):
            # Add to current chunk
            current_chunk.append(sentence)
            # Update chunk embedding (average)
            current_embedding = np.mean([current_embedding[0], sentence_embedding[0]], axis=0).reshape(1, -1)
        else:
            # Yield current chunk if it meets minimum size
            if len(chunk_text) >= min_chunk_size:
                chunk_id = f"{slugify(module_name)}_semantic_{chunk_index}"
                title = f"Semantic Chunk {chunk_index}"
                yield Chunk(
                    id=chunk_id,
                    module=module_name,
                    title=title,
                    content=chunk_text
                )
                chunk_index += 1
            
            # Start new chunk
            current_chunk = [sentence]
            current_embedding = sentence_embedding
    
    # Don't forget the last chunk
    chunk_text = " ".join(current_chunk)
    if len(chunk_text) >= min_chunk_size:
        chunk_id = f"{slugify(module_name)}_semantic_{chunk_index}"
        title = f"Semantic Chunk {chunk_index}"
        yield Chunk(
            id=chunk_id,
            module=module_name,
            title=title,
            content=chunk_text
        )
