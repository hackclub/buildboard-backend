import logging
from collections.abc import Generator
from sqlalchemy.orm import Session
from fastapi import Header, HTTPException, status, Depends
from app.db import SessionLocal
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_auth(Authorization: str = Header(...)) -> None:
    settings = get_settings()
    if Authorization != settings.MASTER_KEY:
        masked_received = f"{Authorization[:4]}...{Authorization[-4:]}" if len(Authorization) > 8 else "SHORT/INVALID"
        logger.warning(f"Auth failed. Expected key starting with {settings.MASTER_KEY[:4]}..., received: {masked_received}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )


def _has_role(db: Session, user_id: str, role_id: str) -> bool:
    from app.models.user_role import UserRole
    return db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first() is not None


def verify_admin(
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> None:
    from app.models.user import User
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not _has_role(db, x_user_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def verify_reviewer(
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> None:
    from app.models.user import User
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not _has_role(db, x_user_id, "reviewer") and not _has_role(db, x_user_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required"
        )


def get_current_user(
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
):
    from app.models.user import User
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
