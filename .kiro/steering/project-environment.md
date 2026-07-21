---
inclusion: always
---

# Project Environment Rules

## Python Virtual Environment

**ALL Python commands for this project MUST use the `.venv` in the project root.**

This project uses Python 3.12. Never use `python`, `python3`, `pip`, or `uvicorn` directly — always route through the `.venv`.

### Windows (cmd) — correct commands

```cmd
.venv\Scripts\python.exe          # run Python
.venv\Scripts\pip.exe             # install packages
.venv\Scripts\uvicorn.exe         # run the server
.venv\Scripts\alembic.exe         # run migrations
.venv\Scripts\pytest.exe          # run tests
```

### PowerShell — correct commands

```powershell
.venv\Scripts\python.exe
.venv\Scripts\pip.exe
```

### Examples

```cmd
# Run the app
.venv\Scripts\uvicorn.exe app.main:app --reload

# Install a package
.venv\Scripts\pip.exe install <package>

# Run migrations
.venv\Scripts\alembic.exe upgrade head

# Run a script
.venv\Scripts\python.exe -m app.some_module

# Run tests
.venv\Scripts\pytest.exe
```

**Never use:**
- `python ...` (uses system Python)
- `pip install ...` (installs into system Python)
- `py -m ...` (may resolve to wrong interpreter)

---

## Codebase Knowledge Graph (Graphify)

When the user asks any question about **how this codebase works**, including:
- "How does X work?"
- "What calls Y?"
- "Where is Z implemented?"
- "Trace the flow through..."
- "What depends on..."
- "Show me the architecture of..."
- "Explain the ingestion pipeline / chat service / etc."

**Before reading individual files, check if `graphify-out/graph.json` exists.**

If `graphify-out/graph.json` exists:
1. Activate the `graphify` skill
2. Use `graphify query "<question>"` to answer from the pre-built knowledge graph
3. Only fall back to direct file reads if the graph query returns insufficient detail

If `graphify-out/graph.json` does not exist:
- Answer from direct file reads as normal
- Optionally suggest the user run `/graphify` to build the knowledge graph for faster future queries

**Why:** The graphify knowledge graph provides richer, cross-file context than reading individual files one at a time. It surfaces relationships, call graphs, and community structure that aren't visible from single-file reads.
