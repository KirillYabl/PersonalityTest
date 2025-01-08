from functools import lru_cache

from pydantic import field_validator, SecretStr
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class SettingsSchema(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        extra="ignore",
    )

    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: SecretStr

    TELEGRAM_BOT_TOKEN: SecretStr
    WEBAPP_URL: str

    APP_SECRET_KEY: SecretStr
    ACCESS_TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24

    SQLALCHEMY_DATABASE_URL: SecretStr | None = None
    SQLALCHEMY_DATABASE_URL_FOR_ALEMBIC: SecretStr | None = None

    @field_validator("SQLALCHEMY_DATABASE_URL", mode="after")
    def build_database_url(cls, value: SecretStr | None, values: ValidationInfo) -> SecretStr:
        postgres_user = values.data.get("POSTGRES_USER").get_secret_value()
        postgres_password = values.data.get("POSTGRES_PASSWORD").get_secret_value()
        postgres_db = values.data.get("POSTGRES_DB").get_secret_value()
        if value is None:
            return SecretStr(f"postgresql+asyncpg://{postgres_user}:{postgres_password}@db/{postgres_db}")
        return SecretStr(value)
    
    @field_validator("SQLALCHEMY_DATABASE_URL_FOR_ALEMBIC", mode="after")
    def build_database_url_for_alembic(cls, value: SecretStr | None, values: ValidationInfo) -> SecretStr:
        postgres_user = values.data.get("POSTGRES_USER").get_secret_value()
        postgres_password = values.data.get("POSTGRES_PASSWORD").get_secret_value()
        postgres_db = values.data.get("POSTGRES_DB").get_secret_value()
        if value is None:
            return SecretStr(f"postgresql://{postgres_user}:{postgres_password}@db/{postgres_db}")
        return SecretStr(value)

@lru_cache
def get_config() -> SettingsSchema:
    return SettingsSchema()


settings = get_config()