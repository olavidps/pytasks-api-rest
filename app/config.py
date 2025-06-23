"""Configuration settings for the application."""

import os
from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """Base application configuration."""

    ENV: str = Field(..., validation_alias="ENVIRONMENT")
    DEBUG: bool = True
    PROJECT_NAME: str = "PyTasks API"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = Field(
        default="development_secret_key_change_in_production",
    )
    DATABASE_URL: PostgresDsn

    class Config:
        """Configuration settings for the application."""

        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG: bool = True


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG: bool = False
    SECRET_KEY: str = Field(
        ..., validation_alias="SECRET_KEY"
    )  # Enforce secret key in prod


class TestingConfig(BaseConfig):
    """Testing configuration."""

    DEBUG: bool = True
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/pytasks_test",
        validation_alias="TEST_DATABASE_URL",
    )


@lru_cache()
def get_settings() -> BaseConfig:
    """Get the correct settings based on the environment."""
    env = os.getenv("ENVIRONMENT", "dev").lower()
    config_map = {
        "dev": DevelopmentConfig,
        "prod": ProductionConfig,
        "test": TestingConfig,
    }
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


settings = get_settings()
