from functools import lru_cache

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class SettingsSchema(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        extra="ignore",
    )

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URL: str | None = None
    SQLALCHEMY_DATABASE_URL_FOR_ALEMBIC: str | None = None

    @field_validator("SQLALCHEMY_DATABASE_URL", mode="after")
    def build_database_url(cls, value: str | None, values: ValidationInfo) -> str:
        postgres_user = values.data.get("POSTGRES_USER")
        postgres_password = values.data.get("POSTGRES_PASSWORD")
        postgres_db = values.data.get("POSTGRES_DB")
        if value is None:
            return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@db/{postgres_db}"
        return value
    
    @field_validator("SQLALCHEMY_DATABASE_URL_FOR_ALEMBIC", mode="after")
    def build_database_url_for_alembic(cls, value: str | None, values: ValidationInfo) -> str:
        postgres_user = values.data.get("POSTGRES_USER")
        postgres_password = values.data.get("POSTGRES_PASSWORD")
        postgres_db = values.data.get("POSTGRES_DB")
        if value is None:
            return f"postgresql://{postgres_user}:{postgres_password}@db/{postgres_db}"
        return value

@lru_cache
def get_config() -> SettingsSchema:
    return SettingsSchema()


settings = get_config()