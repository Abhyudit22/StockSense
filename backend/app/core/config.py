from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: str
    OPENROUTER_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file='../.env', extra='ignore')

settings = Settings()
if settings.DATABASE_URL.startswith('postgresql://'):
    settings.DATABASE_URL = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
