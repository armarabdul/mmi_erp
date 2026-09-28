from typing import List, Optional
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DB_PATH = (PROJECT_ROOT / "mmi_analytics.db").as_posix()

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_NAME: str = "MMI AI Analytics"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Auth
    JWT_SECRET: str = "mmi-super-secure-enterprise-jwt-secret-key-change-in-prod-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # AI Provider
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_REASONING_MODEL: str = "gpt-4o"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
