from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings configuration."""

    PROJECT_NAME: str = "Tron API"
    DESCRIPTION: str = "Микросервис для получения информации об адресах в сети Tron"
    VERSION: str = "1.0.0"

    DATABASE_URL: str = Field()

    TRON_NETWORK: str = "mainnet"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
