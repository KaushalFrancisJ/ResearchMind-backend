"""DOCX parsing facade that delegates to the appropriate chunking strategy."""

from pathlib import Path
from typing import Generator

from app.services.chunking import extract_chunks_from_docx
from app.services.chunking.chunk_models import Chunk


def parse_docx(file_path: str | Path) -> Generator[Chunk, None, None]:
    """Parse a DOCX file and extract structured chunks.
    
    This is a facade that delegates to the heading-based chunker.
    Future implementations could add strategy selection.
    
    Args:
        file_path: Path to DOCX file
        
    Yields:
        Chunk objects extracted from the DOCX file
    """
    # Delegate to heading-based chunker
    yield from extract_chunks_from_docx(str(file_path))
