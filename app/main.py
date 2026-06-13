from fastapi import FastAPI

app = FastAPI(title="RAG Backend")


@app.get("/")
def root():
    return {"status": "ok"}
