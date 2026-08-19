from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USER_AGENT: str
    NEWSAPI_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    SECRET_KEY: str
    CORS_ORIGINS: str

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

settings = Settings()
