"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings shared by the API and background workers."""

    app_name: str = "Enterprise AI Knowledge Assistant"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = Field(
        default="postgresql+psycopg://assistant:assistant@localhost:5432/assistant",
        description="PostgreSQL connection URL.",
    )
    redis_url: str = "redis://localhost:6379/0"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
    # Must be supplied through JWT_SECRET in deployed environments.
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    gemini_api_key: str = ""
    llm_model: str = "gemini-2.5-flash"
    llm_enabled: bool = True
    upload_dir: str = "./data/uploads"
    max_upload_bytes: int = 25 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
