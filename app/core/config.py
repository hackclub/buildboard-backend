from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MASTER_KEY: str
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Hackatime Admin API
    HACKATIME_ADMIN_API_URL: str = "https://hackatime.hackclub.com/api/admin/v1"
    HACKATIME_API_KEY: str | None = None
    
    # Email settings (optional - if not set, OTPs will be logged)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_TLS: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
