"""PDF parsing facade that delegates to the appropriate chunking strategy."""

from pathlib import Path
from typing import Generator

from app.services.chunking import extract_chunks_from_pdf
from app.services.chunking.chunk_models import Chunk


def parse_pdf(file_path: str | Path) -> Generator[Chunk, None, None]:
    """Parse a PDF file and extract structured chunks.
    
    This is a facade that delegates to the heading-based chunker.
    Future implementations could add strategy selection based on PDF structure.
    
    Args:
        file_path: Path to PDF file
        
    Yields:
        Chunk objects extracted from the PDF
    """
    # Delegate to heading-based chunker
    yield from extract_chunks_from_pdf(str(file_path))
