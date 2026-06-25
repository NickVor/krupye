from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    public_base_url: str
    openai_api_key: str | None
    openai_base_url: str | None
    assistant_model: str
    database_path: str
    host: str
    port: int
    log_level: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")

    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")

    return Settings(
        bot_token=bot_token,
        public_base_url=public_base_url,
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        assistant_model=os.getenv("ASSISTANT_MODEL", "gpt-4.1-mini"),
        database_path=os.getenv("DATABASE_PATH", "assistant.sqlite3"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info"),
    )
