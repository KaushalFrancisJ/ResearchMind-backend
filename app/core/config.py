from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_DIALECT: str = "postgresql+psycopg"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USERNAME: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    DEFAULT_DATABASE: str = "postgres"

    RETRIEVAL_TOP_K: int = 5
    
    # File uploads
    UPLOADS_DIR: str = "uploads"

    # Environment: "development" uses Ollama, "production" uses Groq
    ENV: str = "development"

    # HuggingFace Inference API for embeddings
    HF_TOKEN: str = ""
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Ollama settings (development)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_FAST_MODEL: str = "phi4-mini:3.8b-q4_K_M"
    OLLAMA_THINKING_MODEL: str = "phi4-mini-reasoning:3.8b-q4_K_M"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Groq settings (production)
    GROQ_API_KEY: str = ""
    GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"
    GROQ_THINKING_MODEL: str = "qwen-qwq-32b"
    
    # Gemini API — not currently in use, reserved for future providers
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    @property
    def database_url(self) -> str:
        return (
            f"{self.DATABASE_DIALECT}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DEFAULT_DATABASE}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
