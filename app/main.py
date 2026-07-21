from fastapi import FastAPI

from app.api.v1 import chat, documents, health, ingestion
from app.core.logging import setup_logging

# Setup logging
setup_logging()

app = FastAPI(title="RAG Backend")

# Register routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "ok"}
