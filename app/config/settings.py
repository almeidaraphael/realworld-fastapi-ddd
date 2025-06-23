from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    secret_key: str
    debug: bool = False
    env_file: str = ".env"

    model_config = {
        "env_file": ".env",
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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_database_settings() -> DatabaseSettings:
    app_settings = get_app_settings()
    if getattr(app_settings, "env_file", ".env") != ".env":
        load_dotenv(app_settings.env_file, override=True)
    return DatabaseSettings.model_validate({})
