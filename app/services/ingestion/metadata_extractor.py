"""Extract metadata from documents."""

from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document


def extract_pdf_metadata(file_path: str | Path) -> dict:
    """Extract metadata from a PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary containing document metadata
    """
    doc = fitz.open(str(file_path))
    metadata = doc.metadata or {}
    
    result = {
        "title": metadata.get("title"),
        "author": metadata.get("author"),
        "subject": metadata.get("subject"),
        "keywords": metadata.get("keywords"),
        "creator": metadata.get("creator"),
        "producer": metadata.get("producer"),
        "creation_date": metadata.get("creationDate"),
        "modification_date": metadata.get("modDate"),
        "page_count": len(doc),
        "file_size": Path(file_path).stat().st_size,
    }
    
    doc.close()
    return {k: v for k, v in result.items() if v is not None}


def extract_docx_metadata(file_path: str | Path) -> dict:
    """Extract metadata from a DOCX file.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Dictionary containing document metadata
    """
    doc = Document(str(file_path))
    core_props = doc.core_properties
    
    result = {
        "title": core_props.title,
        "author": core_props.author,
        "subject": core_props.subject,
        "keywords": core_props.keywords,
        "comments": core_props.comments,
        "created": core_props.created.isoformat() if core_props.created else None,
        "modified": core_props.modified.isoformat() if core_props.modified else None,
        "last_modified_by": core_props.last_modified_by,
        "revision": core_props.revision,
        "file_size": Path(file_path).stat().st_size,
    }
    
    return {k: v for k, v in result.items() if v is not None}


def extract_metadata(file_path: str | Path) -> dict:
    """Extract metadata from any supported document type.
    
    Args:
        file_path: Path to document file
        
    Returns:
        Dictionary containing document metadata
        
    Raises:
        ValueError: If file type is not supported
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == ".pdf":
        return extract_pdf_metadata(path)
    elif suffix in (".docx", ".doc"):
        return extract_docx_metadata(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
