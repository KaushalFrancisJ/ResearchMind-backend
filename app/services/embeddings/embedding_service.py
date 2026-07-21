from pathlib import Path

import requests

from app.core.config import settings


def embed(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using HuggingFace Inference API.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (each is a list of floats)
        
    Raises:
        ValueError: If HF_TOKEN is not configured
        requests.exceptions.HTTPError: If API request fails
    """
    if not settings.HF_TOKEN:
        raise ValueError("HF_TOKEN not configured in settings")
    
    api_url = f"https://api-inference.huggingface.co/models/{settings.HF_EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
    
    # HuggingFace API accepts either a single string or list of strings
    response = requests.post(
        api_url,
        headers=headers,
        json={"inputs": texts},
        timeout=30
    )
    
    response.raise_for_status()
    embeddings = response.json()
    
    # API returns a list of embeddings for a list input
    # Ensure we always return list[list[float]]
    if isinstance(embeddings, list) and len(embeddings) > 0:
        if isinstance(embeddings[0], list):
            return embeddings
        else:
            # Single embedding returned as flat list - wrap it
            return [embeddings]
    
    return embeddings
