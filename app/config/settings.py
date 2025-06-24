import os
import sys
from enum import Enum

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


def get_environment() -> Environment:
    """Determine the current environment based on various indicators."""
    # Check explicit environment variable first
    if env := os.getenv("APP_ENV"):
        return Environment(env.lower())

    # Check if we're running tests
    if (
        "pytest" in sys.modules
        or any("pytest" in arg for arg in sys.argv)
        or os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("ENV_FILE") == ".env.test"
    ):
        return Environment.TESTING

    # Default to development
    return Environment.DEVELOPMENT


def get_env_file_for_environment(env: Environment) -> str:
    """Get the appropriate .env file for the given environment."""
    if env == Environment.TESTING:
        return ".env.test"
    elif env == Environment.PRODUCTION:
        return ".env.prod"  # For future use
    else:
        return ".env"


# Load environment file based on current environment
_current_env = get_environment()
_env_file = get_env_file_for_environment(_current_env)
load_dotenv(_env_file, override=True)


class AppSettings(BaseSettings):
    secret_key: str
    debug: bool = False
    environment: Environment = _current_env

    model_config = {
        "env_file": _env_file,
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_app_settings() -> AppSettings:
    return AppSettings.model_validate({})


class DatabaseSettings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    environment: Environment = _current_env

    model_config = {
        "env_file": _env_file,
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_test_database(self) -> bool:
        """Check if this is a test database configuration."""
        return self.environment == Environment.TESTING or "test" in self.postgres_db.lower()

    def validate_environment(self) -> None:
        """Validate that we're using the correct database for the environment."""
        if self.environment == Environment.TESTING and not self.is_test_database:
            raise ValueError(
                f"Test environment detected but not using test database. "
                f"DB: {self.postgres_db}, Env: {self.environment}"
            )
        elif self.environment != Environment.TESTING and self.is_test_database:
            raise ValueError(
                f"Non-test environment but using test database. "
                f"DB: {self.postgres_db}, Env: {self.environment}"
            )


def get_database_settings() -> DatabaseSettings:
    settings = DatabaseSettings.model_validate({})
    settings.validate_environment()
    return settings
