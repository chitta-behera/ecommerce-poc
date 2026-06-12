import logging
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-commerce POC API"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # Comma-separated list of allowed CORS origins.
    # Default covers the Vite dev server; override in production.
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Future-proofing for database and cache
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True


settings = Settings()
