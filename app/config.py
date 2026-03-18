"""Application configuration management.

Configuration is loaded from system environment variables only.
No .env files are used.
"""

from functools import lru_cache
from typing import cast

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from system environment variables.

    Required environment variables:
        DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
        JWT_SECRET_KEY

    Optional environment variables (with defaults):
        JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        API_HOST, API_PORT, API_CORS_ORIGINS
        ENVIRONMENT, DEBUG
    """

    model_config = SettingsConfigDict(
        env_file=None,  # Disable .env file loading
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database - Required
    db_host: str
    db_port: int = 3306
    db_name: str = "ingenuity_lab"
    db_user: str = "root"
    db_password: str = ""

    @property
    def database_url(self) -> str:
        """Construct MySQL connection URL."""
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    # Environment
    environment: str = "development"
    debug: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate required settings
        if not self.db_password:
            raise ValueError("DB_PASSWORD environment variable is required")
        if not self.jwt_secret_key or self.jwt_secret_key == "change-this-in-production":
            raise ValueError("JWT_SECRET_KEY environment variable must be set")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
