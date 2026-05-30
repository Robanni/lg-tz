from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    debug: bool = True

    app_title: str = "LG TZ API"
    app_version: str = "0.1.0"
    app_description: str = ""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lg_tz"
    alembic_database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/lg_tz"

    auth_secret_key: str = "change-me-in-production"
    auth_algorithm: str = "HS256"
    auth_access_token_ttl_seconds: int = 900
    auth_refresh_token_ttl_seconds: int = 2_592_000

    cors_allow_origins: str = "*"
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    cors_allow_credentials: bool = True

    def _split(self, value: str) -> list[str]:
        return [v.strip() for v in value.split(",") if v.strip()]

    @property
    def cors_origins(self) -> list[str]:
        return self._split(self.cors_allow_origins)

    @property
    def cors_methods(self) -> list[str]:
        return self._split(self.cors_allow_methods)

    @property
    def cors_headers(self) -> list[str]:
        return self._split(self.cors_allow_headers)

    @model_validator(mode="after")
    def _check_production_secrets(self) -> "AppSettings":
        if not self.debug and self.auth_secret_key == "change-me-in-production":
            raise ValueError("AUTH_SECRET_KEY must be changed from default in production")
        return self


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
