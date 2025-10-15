from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.crud import users as crud

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(verify_auth)])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return crud.create_user(db, user_in)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserRead:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=List[UserRead])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
) -> List[UserRead]:
    return list(crud.list_users(db, skip=skip, limit=limit))


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
) -> UserRead:
    return crud.update_user(db, user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)) -> None:
    crud.delete_user(db, user_id)
    return None
