from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environments(str, Enum):
    DEV = "dev"
    PROD = "prod"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_VER: str = "0.1.0"
    APP_NAME: str = "rsf-orders-service"

    ENVIRONMENT: str = Environments.DEV

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PORT: int = 8000

    DB_URL: str = "sqlite:///:memory:"
    DB_PASSWORD: str | None = None


config = AppConfig()
