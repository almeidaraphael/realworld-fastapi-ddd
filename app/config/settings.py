from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    secret_key: str
    debug: bool = False
    test_mode: bool = False

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
    return DatabaseSettings.model_validate({})


class TestDatabaseSettings(DatabaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "TEST_",
        "extra": "ignore",
    }


def get_test_database_settings() -> TestDatabaseSettings:
    return TestDatabaseSettings.model_validate({})
