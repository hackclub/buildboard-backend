from typing import List, Dict
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth, verify_admin
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.project import ProjectRead
from app.crud import users as crud
from app.models.user import User

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


@router.post("/{user_id}/makeadmin", response_model=UserRead, dependencies=[Depends(verify_admin)])
def make_admin(user_id: str, db: Session = Depends(get_db)) -> UserRead:
    return crud.set_user_admin(db, user_id, True)


@router.get("/{user_id}/projects", response_model=List[ProjectRead])
def list_user_projects(user_id: str, db: Session = Depends(get_db)) -> List[ProjectRead]:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.projects


@router.get("/by-email/{email}")
def get_user_id_by_email(email: str, db: Session = Depends(get_db)) -> dict:
    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id}


@router.get("/{user_id}/exists")
def check_user_exists(user_id: str, db: Session = Depends(get_db)) -> dict:
    user = crud.get_user(db, user_id)
    return {"exists": user is not None}


@router.post("/{user_id}/loggedin", status_code=status.HTTP_200_OK)
def record_login(user_id: str, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    today = date.today().isoformat()
    
    if user.dates_logged_in is None:
        user.dates_logged_in = []
    
    if len(user.dates_logged_in) == 0 or user.dates_logged_in[-1] != today:
        user.dates_logged_in.append(today)
        db.commit()
        return {"message": "Login recorded", "date": today}
    
    return {"message": "Already logged in today", "date": today}


@router.get("/stats/logins")
def get_login_stats(db: Session = Depends(get_db)) -> Dict[str, int]:
    start_date = date(2025, 10, 28)
    today = date.today()
    
    stats = {}
    current_date = start_date
    
    while current_date <= today:
        date_str = current_date.isoformat()
        users = db.query(User).filter(User.dates_logged_in.contains([date_str])).all()
        stats[date_str] = len(users)
        current_date += timedelta(days=1)
    
    return stats
