from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, data: UserCreate) -> User:
    user = User(**data.model_dump())
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or Slack ID already exists"
        )
    return user


def get_user(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def list_users(db: Session, skip: int = 0, limit: int = 100) -> Sequence[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: str, data: UserUpdate) -> User:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or Slack ID already exists"
        )
    return user


def delete_user(db: Session, user_id: str) -> None:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
