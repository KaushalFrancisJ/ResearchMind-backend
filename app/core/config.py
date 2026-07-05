from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_DIALECT: str = "postgresql+psycopg"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USERNAME: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    DEFAULT_DATABASE: str = "postgres"

    RETRIEVAL_TOP_K: int = 5

    # Environment: "development" uses Ollama, "production" uses Groq
    ENV: str = "development"

    # Ollama settings (development)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_FAST_MODEL: str = "phi4-mini:3.8b-q4_K_M"
    OLLAMA_THINKING_MODEL: str = "phi4-mini-reasoning:3.8b-q4_K_M"

    # Groq settings (production)
    GROQ_API_KEY: str = ""
    GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"
    GROQ_THINKING_MODEL: str = "qwen-qwq-32b"

    @property
    def database_url(self) -> str:
        return (
            f"{self.DATABASE_DIALECT}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DEFAULT_DATABASE}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
