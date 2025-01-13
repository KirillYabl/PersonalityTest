from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from resources.schema_constants import Stand


class SettingsSchema(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        extra="ignore",
    )

    STAND: str

    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: SecretStr
    DB_LABEL: str

    TELEGRAM_BOT_TOKEN: SecretStr
    WEBAPP_URL: str

    APP_SECRET_KEY: SecretStr
    ACCESS_TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24

    QUIZ_UUID: str

    SQLALCHEMY_DATABASE_URL: SecretStr | None = None
    SQLALCHEMY_DATABASE_URL_FOR_ALEMBIC: SecretStr | None = None

    @field_validator("SQLALCHEMY_DATABASE_URL", mode="after")
    def build_database_url(cls, value: SecretStr | None, values: ValidationInfo) -> SecretStr:
        postgres_user = values.data.get("POSTGRES_USER").get_secret_value()
        postgres_password = values.data.get("POSTGRES_PASSWORD").get_secret_value()
        postgres_db = values.data.get("POSTGRES_DB").get_secret_value()
        db_label = values.data.get("DB_LABEL")
        if value is None:
            return SecretStr(f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{db_label}/{postgres_db}")
        return SecretStr(value)

    @field_validator("SQLALCHEMY_DATABASE_URL_FOR_ALEMBIC", mode="after")
    def build_database_url_for_alembic(cls, value: SecretStr | None, values: ValidationInfo) -> SecretStr:
        postgres_user = values.data.get("POSTGRES_USER").get_secret_value()
        postgres_password = values.data.get("POSTGRES_PASSWORD").get_secret_value()
        postgres_db = values.data.get("POSTGRES_DB").get_secret_value()
        db_label = values.data.get("DB_LABEL")
        if value is None:
            return SecretStr(f"postgresql://{postgres_user}:{postgres_password}@{db_label}/{postgres_db}")
        return SecretStr(value)

    @field_validator("STAND", mode="before")
    def validate_stand(cls, value: str) -> str:
        if value not in Stand.values():
            raise ValueError(f"STAND must be one of {', '.join(Stand.values())}")
        return value


@lru_cache
def get_config() -> SettingsSchema:
    return SettingsSchema()


settings = get_config()
