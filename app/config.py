from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # env_ignore_empty lets blank lines like `YAHOO_GAME_ID=` count as "unset"
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore", env_ignore_empty=True)

    yahoo_consumer_key: str
    yahoo_consumer_secret: str
    yahoo_redirect_uri: str
    session_secret: str
    encryption_key: str
    redis_url: str = "redis://localhost:6379/0"

    frontend_url: str = "/"
    cors_origins: str = ""  # comma-separated
    cookie_secure: bool = True

    yahoo_game_id: int | None = None
    cache_ttl_seconds: int = 300


settings = Settings()
