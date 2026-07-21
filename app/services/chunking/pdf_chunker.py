from pathlib import Path
from typing import Generator

import fitz

from .chunk_models import Chunk, slugify


def extract_chunks_from_pdf(file_path: str) -> Generator[Chunk, None, None]:
    path = Path(file_path)
    module_name = path.stem
    doc = fitz.open(file_path)

    # Collect lines (joined spans) with dominant font size and bold flag
    all_lines = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = " ".join(s["text"].strip() for s in spans)
                # Use the dominant (most common) size in the line
                dominant_size = max(set(s["size"] for s in spans), key=[s["size"] for s in spans].count)
                any_bold = any(bool(s["flags"] & 16) for s in spans)
                all_lines.append({"text": text, "size": dominant_size, "bold": any_bold})

    if not all_lines:
        doc.close()
        return

    # Detect body font size from most common size across all lines
    sizes = [l["size"] for l in all_lines]
    body_size = max(set(sizes), key=sizes.count)
    heading_threshold = body_size * 1.05

    current_heading = None
    current_content = []

    for line in all_lines:
        text = line["text"]
        is_bold = line["bold"]
        # Must be both larger AND bold, or bold+larger-than-body (catches slight size bumps)
        is_heading = is_bold and line["size"] > body_size

        if is_heading:
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
            if current_heading:  # only collect content once a heading is found
                current_content.append(text)

    if current_heading and current_content:
        yield Chunk(
            id=f"{slugify(module_name)}_{slugify(current_heading)}",
            module=module_name,
            title=current_heading,
            content="\n".join(current_content),
        )

    doc.close()
