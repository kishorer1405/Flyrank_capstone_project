from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FlyRank Lead-Capture Platform"
    environment: str = "development"
    base_url: str = "http://localhost:8000"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/flyrank"
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5500", "http://127.0.0.1:5500"])
    rate_limit: str = "5/minute"
    geo_provider_a_url: str = "http://ip-api.com/json/{ip}"
    geo_provider_b_url: str = "https://ipapi.co/{ip}/json/"
    geo_provider_a_mode: str = "real"
    geo_provider_b_mode: str = "real"
    side_effect_mode: str = "console"
    side_effect_fail: bool = False
    job_poll_seconds: float = 2.0
    max_payload_bytes: int = 16_384
    config_cache_seconds: int = 60
    widget_cache_seconds: int = 31536000
    geo_timeout_seconds: float = 3.0
    max_job_attempts: int = 3

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return value

    @property
    def widget_script_url(self) -> str:
        return f"{self.base_url}/widget.v1.js"

@lru_cache
def get_settings() -> Settings:
    return Settings()
