from functools import lru_cache

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(alias="POSTGRES_PORT")
    postgres_username: str = Field(alias="POSTGRES_USERNAME")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_password: SecretStr = Field(alias="POSTGRES_PASSWORD")

    gis_api_base_url: str = Field(alias="GIS_API_BASE_URL")
    gis_api_key: str = Field(alias="GIS_API_KEY")
    gis_api_timeout_seconds: int = Field(default=30, alias="GIS_API_TIMEOUT_SECONDS")

    max_token: SecretStr = Field(alias="MAX_TOKEN")

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @property
    def postgres_asyncpg_dsn(self) -> str:
        password = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_username}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()