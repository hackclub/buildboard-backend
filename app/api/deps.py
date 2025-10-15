from collections.abc import Generator
from sqlalchemy.orm import Session
from fastapi import Header, HTTPException, status
from app.db import SessionLocal
from app.core.config import get_settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_auth(api_key: str = Header(...)) -> None:
    settings = get_settings()
    if api_key != settings.MASTER_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
