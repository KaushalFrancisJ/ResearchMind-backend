# ResearchMind Backend

A RAG (Retrieval-Augmented Generation) backend built with FastAPI, PostgreSQL, and pgvector.

## Requirements

- [uv](https://docs.astral.sh/uv/) — Python package manager
- PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension

## Setup

**1. Install dependencies**
```bash
uv sync
```

**2. Configure environment**
```bash
cp .env.example .env
```
Fill in your credentials in `.env`:
```env
DATABASE_DIALECT=postgresql+psycopg
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=yourpassword
DEFAULT_DATABASE=researchmind
```

**3. Create the database**

Connect to PostgreSQL and run:
```sql
CREATE DATABASE researchmind;
```

## Database Migrations

All migration commands are run from the `backend/` directory.

| Command | Purpose |
|---|---|
| `uv run alembic upgrade head` | Apply all migrations (create all tables) |
| `uv run alembic downgrade base` | Roll back all migrations (drop all tables) |
| `uv run alembic downgrade -1` | Roll back the last migration only |
| `uv run alembic current` | Show the current migration revision |
| `uv run alembic history` | List all migrations |
| `uv run alembic revision -m "description"` | Create a new empty migration file |

## Running the Server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Database Schema

| Table | Description |
|---|---|
| `sessions` | Research sessions |
| `documents` | Uploaded documents (unique by hash) |
| `session_documents` | Junction table linking sessions to documents |
| `document_chunks` | Chunked document content with vector embeddings |
| `session_chat` | Chat messages per session with RAG context |
| `session_summary` | Rolling summaries of chat history |
| `chat_evaluation` | Faithfulness and relevancy scores per chat response |

## Project Structure

```
backend/
├── alembic/                  # Migration environment
│   ├── versions/             # Migration files
│   └── env.py                # Alembic environment config
├── app/
│   ├── api/v1/               # API route handlers
│   ├── core/                 # Config, logging, security
│   ├── db/                   # Database session and base
│   ├── models/               # SQLAlchemy ORM models
│   ├── repositories/         # Database query logic
│   ├── schemas/              # Pydantic request/response schemas
│   └── services/             # Business logic (chunking, embeddings, LLM, retrieval)
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
├── .env.example              # Environment variable template
├── alembic.ini               # Alembic configuration
└── pyproject.toml            # Project dependencies
```
