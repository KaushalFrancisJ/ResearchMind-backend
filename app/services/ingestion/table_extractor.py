"""Extract tables from documents."""

from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from docx.table import Table


def extract_tables_from_docx(file_path: str | Path) -> list[dict]:
    """Extract tables from a DOCX file.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        List of table dictionaries with rows and cells
    """
    doc = Document(str(file_path))
    tables_data = []
    
    for table_idx, table in enumerate(doc.tables):
        rows_data = []
        for row in table.rows:
            cells_data = [cell.text.strip() for cell in row.cells]
            rows_data.append(cells_data)
        
        tables_data.append({
            "table_index": table_idx,
            "row_count": len(table.rows),
            "col_count": len(table.columns) if table.rows else 0,
            "data": rows_data
        })
    
    return tables_data


def extract_tables_from_pdf(file_path: str | Path) -> list[dict]:
    """Extract tables from a PDF file using PyMuPDF's table detection.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of table dictionaries with rows and cells
    """
    doc = fitz.open(str(file_path))
    tables_data = []
    table_index = 0
    
    for page_num, page in enumerate(doc):
        # Find tables on the page
        tables = page.find_tables()
        
        for table in tables:
            # Extract table data
            rows_data = []
            for row in table.extract():
                rows_data.append([cell or "" for cell in row])
            
            tables_data.append({
                "table_index": table_index,
                "page_number": page_num + 1,
                "row_count": len(rows_data),
                "col_count": len(rows_data[0]) if rows_data else 0,
                "data": rows_data
            })
            table_index += 1
    
    doc.close()
    return tables_data


def extract_tables(file_path: str | Path) -> list[dict]:
    """Extract tables from any supported document type.
    
    Args:
        file_path: Path to document file
        
    Returns:
        List of table dictionaries
        
    Raises:
        ValueError: If file type is not supported
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == ".pdf":
        return extract_tables_from_pdf(path)
    elif suffix in (".docx", ".doc"):
        return extract_tables_from_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
