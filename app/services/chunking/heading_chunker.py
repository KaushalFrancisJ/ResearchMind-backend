from pathlib import Path
from typing import Generator

from docx import Document
from docx.document import Document as DocumentClass
from docx.table import Table
from docx.text.paragraph import Paragraph

from .chunk_models import Chunk, slugify

IGNORE_SECTIONS = {
    "Application User Manual",
    "Document Conventions",
    "Reading Guide",
}


def _iter_block_items(doc: DocumentClass):
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, doc)
        elif child.tag.endswith("}tbl"):
            yield Table(child, doc)


def _table_to_markdown(table: Table) -> str:
    rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
    if not rows:
        return ""
    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join(["---"] * len(rows[0])) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join([header, separator] + body)


def extract_chunks_from_docx(file_path: str) -> Generator[Chunk, None, None]:
    path = Path(file_path)
    module_name = path.stem
    doc = Document(file_path)

    current_heading = None
    current_content = []

    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue

            if block.style.name.startswith("Heading"):
                if current_heading and current_content and current_heading not in IGNORE_SECTIONS:
                    yield Chunk(
                        id=f"{slugify(module_name)}_{slugify(current_heading)}",
                        module=module_name,
                        title=current_heading,
                        content="\n".join(current_content),
                    )
                current_heading = text
                current_content = []
            else:
                current_content.append(text)

        elif isinstance(block, Table):
            table_md = _table_to_markdown(block)
            if table_md:
                current_content.append(table_md)

    if current_heading and current_content and current_heading not in IGNORE_SECTIONS:
        yield Chunk(
            id=f"{slugify(module_name)}_{slugify(current_heading)}",
            module=module_name,
            title=current_heading,
            content="\n".join(current_content),
        )
