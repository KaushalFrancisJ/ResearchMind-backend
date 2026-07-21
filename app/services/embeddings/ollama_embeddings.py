import ollama

from app.core.config import settings


def embed_ollama(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Ollama's embedding endpoint.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (each is a list of floats)
    """
    client = ollama.Client(host=settings.OLLAMA_URL)
    embeddings = []
    
    for text in texts:
        response = client.embeddings(
            model=settings.OLLAMA_EMBEDDING_MODEL,
            prompt=text
        )
        embeddings.append(response["embedding"])
    
    return embeddings
