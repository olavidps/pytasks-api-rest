"""Configuration settings for the application."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PyTasks API"

    # Environment
    ENV: str = Field(default="dev", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/pytasks",
        env="DATABASE_URL",
        description="PostgreSQL connection string",
    )

    # Security
    SECRET_KEY: str = Field(
        default="development_secret_key_change_in_production", env="SECRET_KEY"
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",  # This allows extra environment variables to be ignored
    }


# Create settings instance
settings = Settings()
