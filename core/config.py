from functools import lru_cache

from pydantic_settings import BaseSettings

class SettingsSchema(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite+aiosqlite:///database.db"

    class Config:
        env_file = '.env'

@lru_cache
def get_config() -> SettingsSchema:
    return SettingsSchema()


settings = get_config()