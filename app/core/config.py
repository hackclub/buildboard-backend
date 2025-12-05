from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MASTER_KEY: str
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
