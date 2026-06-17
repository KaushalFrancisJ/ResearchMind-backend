import re
from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    module: str
    title: str
    content: str


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9|aum]+", "_", text.lower()).strip("_")
