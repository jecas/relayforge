from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RelayForge"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    alpha_base_url: str = "http://mock-provider:9000"
    alpha_client_id: str = "relayforge"
    alpha_client_secret: str = "development-secret"
    alpha_timeout_seconds: float = 5.0

    provider_max_attempts: int = 3
    provider_retry_base_delay_seconds: float = 0.25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
