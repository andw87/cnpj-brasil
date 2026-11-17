"""Runtime settings, read from environment variables prefixed CNPJBENCH_ (or .env)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CNPJBENCH_", env_file=PROJECT_ROOT / ".env", extra="ignore"
    )

    mongo_uri: str = "mongodb://127.0.0.1:27017"
    mongo_db: str = "cnpjbench"
    seed_file: Path = Path("data/seed/seed_companies.jsonl")
    catalog_file: Path = Path("catalog/sources.yaml")
    user_agent: str = "cnpjbench/0.1 (research benchmark)"
    http_timeout_s: float = 20.0
    max_retries: int = 2
    max_backoff_s: float = 120.0
    s10_token: str = ""

    def resolve(self, p: Path) -> Path:
        return p if p.is_absolute() else PROJECT_ROOT / p


@lru_cache
def get_settings() -> Settings:
    return Settings()
