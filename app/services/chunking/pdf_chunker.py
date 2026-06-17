from pathlib import Path
from typing import Generator

import fitz

from .chunk_models import Chunk, slugify


def extract_chunks_from_pdf(file_path: str) -> Generator[Chunk, None, None]:
    path = Path(file_path)
    module_name = path.stem
    doc = fitz.open(file_path)

    # Collect all text spans with font sizes
    all_blocks = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        all_blocks.append({"text": text, "size": span["size"]})

    if not all_blocks:
        doc.close()
        return

    # Detect heading threshold from most common (body) font size
    sizes = [b["size"] for b in all_blocks]
    body_size = max(set(sizes), key=sizes.count)
    heading_threshold = body_size * 1.15

    current_heading = None
    current_content = []

    for block in all_blocks:
        text = block["text"]

        # Skip noise: page numbers, footers, isolated short tokens
        if len(text.split()) < 4 and block["size"] <= body_size:
            continue

        if block["size"] >= heading_threshold:
            if current_heading and current_content:
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

    if current_heading and current_content:
        yield Chunk(
            id=f"{slugify(module_name)}_{slugify(current_heading)}",
            module=module_name,
            title=current_heading,
            content="\n".join(current_content),
        )

    doc.close()
