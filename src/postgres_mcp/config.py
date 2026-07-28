"""
Centralized application configuration.

Why this file exists:
All environment-dependent values (DB URL, API keys, log level) are read
ONCE here into a typed, validated object. Every other module imports
`settings` from here instead of calling os.getenv() directly. This gives
us:
  - a single source of truth
  - startup-time validation (fail fast if DATABASE_URL is missing)
  - IDE autocomplete + type checking on config values
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    log_level: str = "INFO"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    lru_cache ensures the .env file is parsed only once per process,
    not on every call to get_settings(). Every module that needs config
    calls get_settings() rather than importing a module-level singleton,
    which makes testing easier (you can clear the cache and inject
    different env vars in tests).
    """
    return Settings()