"""
Config settings and environment variable handling.
"""

from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "civicly-ai"
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

settings = Settings()
