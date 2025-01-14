"""
Config settings and environment variable handling.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "civicly-ai"
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
