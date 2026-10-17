import logging
import os
from datetime import timedelta
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(dotenv_path="./.env")


def setup_logging():
    """Configure basic logging for the application."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


class LLMSettings(BaseModel):
    """Base settings for Language Model configurations."""

    temperature: float = 0.0
    max_tokens: Optional[int] = None
    max_retries: int = 3


class OpenRouterSettings(LLMSettings):
    """OpenRouter-specific settings extending LLMSettings."""

    api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    base_url: str = Field(default_factory=lambda: os.getenv("OPENROUTER_URL"))
    default_model: str = Field(default="openai/gpt-oss-120b")
    embedding_model: str = Field(default="text-embedding-3-small")

    GPT_OSS_INPUT_PRICE: float = 0.030
    GPT_OSS_OUTPUT_PRICE: float = 0.17
    GPT_NANO_INPUT_PRICE: float = 0.10
    GPT_NANO_OUTPUT_PRICE: float = 0.40

class GroqSettings(LLMSettings):
    """Groq-specific settings extending LLMSettings."""

    api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    base_url: str = Field(default_factory=lambda: os.getenv("GROQ_URL"))
    default_model: str = Field(default="openai/gpt-oss-120b")

class GoogleSettings(LLMSettings):
    """Groq-specific settings extending LLMSettings."""

    api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    base_url: str = Field(default_factory=lambda: os.getenv("GOOGLE_URL"))
    default_model: str = Field(default="gemma-4-31b")

class DatabaseSettings(BaseModel):
    """Database connection settings."""

    postgresql_url: str = Field(default_factory=lambda: os.getenv("POSTGRESQL_URL"))

class AgentSettings(BaseModel):
    """Settings for Retrieval Agent"""

    max_retries: int = 3
    max_iterations: int = 8

class LangfuseSettings(BaseModel):
    """Settings for Langfuse observability."""

    secret_key: str = Field(default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY"))
    public_key: str = Field(default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY"))
    host: str = Field(default_factory=lambda: os.getenv("LANGFUSE_HOST"))

class Settings(BaseModel):
    """Main settings class combining all sub-settings."""

    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    google: GoogleSettings = Field(default_factory=GoogleSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    langfuse: LangfuseSettings = Field(default_factory=LangfuseSettings)


@lru_cache()
def get_settings() -> Settings:
    """Create and return a cached instance of the Settings."""
    settings = Settings()
    setup_logging()
    return settings