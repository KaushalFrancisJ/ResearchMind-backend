from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_DIALECT: str = "postgresql+psycopg"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USERNAME: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    DEFAULT_DATABASE: str = "postgres"

    RETRIEVAL_TOP_K: int = 5

    @property
    def database_url(self) -> str:
        return (
            f"{self.DATABASE_DIALECT}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DEFAULT_DATABASE}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
