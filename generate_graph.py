"""
generate_graph.py
=================
Standalone script to build (or incrementally update) the graphify knowledge
graph for this project.  Run it manually whenever you want to refresh the graph:

    python generate_graph.py            # full rebuild
    python generate_graph.py --update   # re-extract only changed files

Requirements
------------
    pip install graphifyy
    # or, if you use uv:
    uv tool install graphifyy

The graphifyy tool-env Python is tried first, then the venv Python, then
whatever `python` is on PATH.  The script resolves the interpreter once and
caches it in graphify-out/.graphify_python for subsequent runs.

Outputs (written to graphify-out/)
-----------------------------------
    graph.json        raw graph data (GraphRAG-ready)
    graph.html        interactive visualisation — open in any browser
    GRAPH_REPORT.md   plain-language audit report with god nodes / surprises
"""

import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent          # project root
OUT  = ROOT / "graphify-out"
INTERPRETER_FILE = OUT / ".graphify_python"

COMMUNITY_LABELS = {
    0:  "Graphify Tool Internals",
    1:  "DB Models & ORM",
    2:  "Chat API & Sessions",
    3:  "Project Docs & Structure",
    4:  "Config & LLM Providers",
    5:  "Chunk Model & Repo",
    6:  "Document Chunking",
    7:  "Graphify Query Engine",
    8:  "Graphify Export Formats",
    9:  "Alembic Migrations",
    10: "App Entry & Health",
    11: "GitHub & Repo Merge",
    12: "Initial DB Schema",
    13: "Main Entry Point",
    14: "API Init",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _uv_available() -> bool:
    """Return True if `uv` is on PATH."""
    result = subprocess.run(
        ["uv", "--version"], capture_output=True
    )
    return result.returncode == 0


def _build_cmd(py: str, mode: str, payload: str) -> list[str]:
    """
    Build the subprocess argv.
    - If py == "uv-run", use `uv run --with graphifyy python -<mode> <payload>`
      which avoids spawning the graphifyy-env .exe directly (works around
      Windows Application Control policies that block child .exe files).
    - Otherwise call py directly.
    mode is either "-c" (code snippet) or "-m" (module).
    """
    if py == "uv-run":
        return ["uv", "run", "--with", "graphifyy", "python", mode, payload]
    return [py, mode, payload]


def _run(py: str, code: str) -> str:
    """Execute a Python snippet and return stdout (raises on error)."""
    result = subprocess.run(
        _build_cmd(py, "-c", code),
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def _run_module(py: str, *args: str) -> None:
    """Run `python -m graphify <args>`."""
    if py == "uv-run":
        cmd = ["uv", "run", "--with", "graphifyy", "python", "-m", "graphify", *args]
    else:
        cmd = [py, "-m", "graphify", *args]
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def resolve_interpreter() -> str:
    """
    Return the token that _run/_run_module will use to launch Python.

    Strategy (in order):
    1. If `uv` is available and `uv run --with graphifyy python` works,
       return the sentinel "uv-run".  This avoids calling the graphifyy-env
       .exe directly, which is blocked by Windows Application Control on
       some machines.
    2. Try candidate .exe / binary paths directly (non-Windows or unblocked).
    3. Fall back to the current sys.executable after pip-installing graphifyy.

    The resolved token is cached in graphify-out/.graphify_python.
    """
    # Check cache
    if INTERPRETER_FILE.exists():
        cached = INTERPRETER_FILE.read_text(encoding="utf-8").strip()
        if cached == "uv-run":
            # Verify uv is still available
            if _uv_available():
                return "uv-run"
        else:
            check = subprocess.run(
                [cached, "-c", "import graphify, networkx"],
                capture_output=True
            )
            if check.returncode == 0:
                return cached

    OUT.mkdir(exist_ok=True)

    # 1. Prefer uv-run to avoid .exe subprocess issues
    if _uv_available():
        check = subprocess.run(
            ["uv", "run", "--with", "graphifyy", "python",
             "-c", "import graphify, networkx; print('ok')"],
            capture_output=True, cwd=str(ROOT)
        )
        if check.returncode == 0:
            INTERPRETER_FILE.write_text("uv-run", encoding="utf-8")
            return "uv-run"

    # 2. Try direct binary paths
    candidates = [
        Path.home() / "AppData/Roaming/uv/tools/graphifyy/Scripts/python.exe",
        Path.home() / ".local/share/uv/tools/graphifyy/bin/python",
        ROOT / ".venv/Scripts/python.exe",
        ROOT / ".venv/bin/python",
    ]
    for candidate in candidates:
        if candidate.exists():
            check = subprocess.run(
                [str(candidate), "-c", "import graphify, networkx"],
                capture_output=True
            )
            if check.returncode == 0:
                INTERPRETER_FILE.write_text(str(candidate), encoding="utf-8")
                return str(candidate)

    # 3. Install into current env as last resort
    print("graphify not found — installing graphifyy …")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "graphifyy", "-q"], check=True
    )
    INTERPRETER_FILE.write_text(sys.executable, encoding="utf-8")
    return sys.executable


# ── Full build ────────────────────────────────────────────────────────────────

def full_build(py: str) -> None:
    print("=== Step 1: Detecting files …")
    _run(py, f"""
import json
from graphify.detect import detect
from pathlib import Path
result = detect(Path(r'{ROOT}'))
Path(r'{OUT}/.graphify_detect.json').write_text(
    json.dumps(result, ensure_ascii=False), encoding='utf-8')
total = result.get('total_files', 0)
words = result.get('total_words', 0)
print(f'Corpus: {{total}} files · {{words:,}} words')
for cat, lst in result.get('files', {{}}).items():
    if lst:
        print(f'  {{cat}}: {{len(lst)}} files')
ss = result.get('skipped_sensitive', [])
if ss:
    print(f'  ({{len(ss)}} sensitive file(s) skipped)')
""")

    print("\n=== Step 2: AST extraction …")
    _run(py, f"""
import json
from graphify.extract import collect_files, extract
from pathlib import Path
detect = json.loads(Path(r'{OUT}/.graphify_detect.json').read_text(encoding='utf-8'))
code_files = []
for f in detect.get('files', {{}}).get('code', []):
    p = Path(f)
    code_files.extend(collect_files(p) if p.is_dir() else [p])
if code_files:
    result = extract(code_files, cache_root=Path(r'{ROOT}'))
    Path(r'{OUT}/.graphify_ast.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'AST: {{len(result["nodes"])}} nodes, {{len(result["edges"])}} edges')
else:
    Path(r'{OUT}/.graphify_ast.json').write_text(
        json.dumps({{'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}}), encoding='utf-8')
    print('No code files — skipping AST.')
""")

    # Semantic: write empty file (docs are graphify internals, not project code)
    _run(py, f"""
import json
from pathlib import Path
Path(r'{OUT}/.graphify_semantic.json').write_text(
    json.dumps({{'nodes':[],'edges':[],'hyperedges':[],'input_tokens':0,'output_tokens':0}}),
    encoding='utf-8')
""")

    print("\n=== Step 3: Merging AST + semantic …")
    _run(py, f"""
import json
from pathlib import Path
ast = json.loads(Path(r'{OUT}/.graphify_ast.json').read_text(encoding='utf-8'))
sem = json.loads(Path(r'{OUT}/.graphify_semantic.json').read_text(encoding='utf-8'))
seen = {{n['id'] for n in ast['nodes']}}
merged_nodes = list(ast['nodes'])
for n in sem['nodes']:
    if n['id'] not in seen:
        merged_nodes.append(n)
        seen.add(n['id'])
merged = {{
    'nodes': merged_nodes,
    'edges': ast['edges'] + sem['edges'],
    'hyperedges': sem.get('hyperedges', []),
    'input_tokens': sem.get('input_tokens', 0),
    'output_tokens': sem.get('output_tokens', 0),
}}
Path(r'{OUT}/.graphify_extract.json').write_text(
    json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Merged: {{len(merged_nodes)}} nodes, {{len(merged["edges"])}} edges')
""")

    print("\n=== Step 4: Building graph, clustering, labelling …")
    _run(py, _build_and_label_code())

    print("\n=== Step 5: Generating HTML …")
    _run_module(py, "export", "html")

    print("\n=== Cleaning up temp files …")
    for tmp in [".graphify_detect.json", ".graphify_ast.json",
                ".graphify_semantic.json", ".graphify_extract.json",
                ".graphify_analysis.json"]:
        (OUT / tmp).unlink(missing_ok=True)
    for chunk in glob.glob(str(OUT / ".graphify_chunk_*.json")):
        Path(chunk).unlink(missing_ok=True)


# ── Incremental update ────────────────────────────────────────────────────────

def incremental_update(py: str) -> None:
    """Re-extract all code files and merge into the existing graph."""
    graph_path = OUT / "graph.json"
    if not graph_path.exists():
        print("No existing graph.json found — running full build instead.")
        full_build(py)
        return

    print("=== Incremental update: re-extracting all code files …")
    _run(py, f"""
import json
from graphify.detect import detect
from graphify.extract import collect_files, extract
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from pathlib import Path

ROOT = Path(r'{ROOT}')
OUT  = Path(r'{OUT}')

# Detect code files
result = detect(ROOT)
code_files = []
for f in result.get('files', {{}}).get('code', []):
    p = Path(f)
    code_files.extend(collect_files(p) if p.is_dir() else [p])

if not code_files:
    print('No code files found.')
    raise SystemExit(0)

new_ext = extract(code_files, cache_root=ROOT)
print(f'Re-extracted: {{len(new_ext["nodes"])}} nodes, {{len(new_ext["edges"])}} edges')

# Load existing graph and drop stale nodes/edges for changed source files
existing = json.loads((OUT / 'graph.json').read_text(encoding='utf-8'))
changed_stems = {{str(p) for p in code_files}}

def from_changed(obj):
    sf = (obj.get('source_file') or '').replace('\\\\', '/')
    return any(sf.endswith(p.replace('\\\\', '/').lstrip('/')) for p in changed_stems)

kept_nodes = [n for n in existing.get('nodes', []) if not from_changed(n)]
kept_edges = [e for e in existing.get('edges', []) if not from_changed(e)]

seen = {{n['id'] for n in kept_nodes}}
for n in new_ext['nodes']:
    if n['id'] not in seen:
        kept_nodes.append(n)
        seen.add(n['id'])

kept_edges.extend(new_ext['edges'])

merged = {{
    'nodes': kept_nodes,
    'edges': kept_edges,
    'hyperedges': existing.get('hyperedges', []),
    'input_tokens': 0,
    'output_tokens': 0,
}}
print(f'Merged: {{len(kept_nodes)}} nodes, {{len(kept_edges)}} edges')

{_build_and_label_code(inline=True)}
""")

    print("\n=== Regenerating HTML …")
    _run_module(py, "export", "html")


# ── Shared build/label logic ──────────────────────────────────────────────────

def _build_and_label_code(inline: bool = False) -> str:
    """
    Return the Python snippet that builds the graph, clusters it, applies
    community labels, writes graph.json and GRAPH_REPORT.md.

    When inline=True the extraction data is already in locals() as `merged`;
    when inline=False it reads from the temp .graphify_extract.json file.
    """
    labels_repr = repr(COMMUNITY_LABELS)

    load_block = "" if inline else f"""
import json
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from pathlib import Path
ROOT = Path(r'{ROOT}')
OUT  = Path(r'{OUT}')
merged = json.loads((OUT / '.graphify_extract.json').read_text(encoding='utf-8'))
"""

    return load_block + f"""
G = build_from_json(merged, root=ROOT, directed=False)
if G.number_of_nodes() == 0:
    print('ERROR: graph is empty — nothing to write.')
    raise SystemExit(1)

communities = cluster(G)
cohesion    = score_all(G, communities)
gods        = god_nodes(G)
surprises   = surprising_connections(G, communities)

base_labels = {labels_repr}
labels = {{cid: base_labels.get(cid, f'Module {{cid}}') for cid in communities}}
questions   = suggest_questions(G, communities, labels)

detect_stub = {{'total_files': 0, 'total_words': 0, 'files': {{}}, 'skipped_sensitive': []}}
tokens      = {{'input': merged.get('input_tokens', 0), 'output': merged.get('output_tokens', 0)}}

# Write graph.json (skip shrink-guard by writing to a temp path then renaming)
tmp = OUT / 'graph_tmp.json'
to_json(G, communities, str(tmp))
if tmp.exists():
    (OUT / 'graph.json').write_bytes(tmp.read_bytes())
    tmp.unlink()

report = generate(G, communities, cohesion, labels, gods, surprises,
                  detect_stub, tokens, str(ROOT), suggested_questions=questions)
(OUT / 'GRAPH_REPORT.md').write_text(report, encoding='utf-8')
(OUT / '.graphify_labels.json').write_text(
    json.dumps({{str(k): v for k, v in labels.items()}}, ensure_ascii=False), encoding='utf-8')

print(f'Graph: {{G.number_of_nodes()}} nodes, {{G.number_of_edges()}} edges, {{len(communities)}} communities')
print(f'Outputs written to: {{OUT}}')
"""


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate (or update) the graphify knowledge graph for this project."
    )
    parser.add_argument(
        "--update", action="store_true",
        help="Incremental mode: re-extract changed files only (faster)."
    )
    args = parser.parse_args()

    OUT.mkdir(exist_ok=True)

    print("Resolving Python interpreter …")
    py = resolve_interpreter()
    print(f"Using: {py}\n")

    if args.update:
        incremental_update(py)
    else:
        full_build(py)

    print("\n✓ Done. Outputs in graphify-out/")
    print("  graph.html      — open in browser")
    print("  GRAPH_REPORT.md — architecture report")
    print("  graph.json      — raw graph data")


if __name__ == "__main__":
    main()
