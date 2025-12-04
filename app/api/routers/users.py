from typing import List, Dict
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, status, HTTPException, Header
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth, verify_admin
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserPublicRead
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


@router.get("/handle/{handle}", response_model=UserRead)
def get_user_by_handle(
    handle: str,
    x_user_id: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> UserRead:
    user = crud.get_user_by_handle(db, handle)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Privacy check
    # If user is public, allow access
    # If user is private, only allow if requester is the owner
    if not user.is_public:
        if not x_user_id or x_user_id != user.user_id:
            raise HTTPException(
                status_code=403,
                detail="This profile is private"
            )
            
    return user


@router.get("", response_model=List[UserPublicRead])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
) -> List[UserPublicRead]:
    """List users - returns public info only (no PII like addresses/emails)"""
    return list(crud.list_users(db, skip=skip, limit=limit))


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> UserRead:
    # Ownership check: users can only update their own profile (admins can update anyone)
    requesting_user = crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    
    if x_user_id != user_id and not requesting_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # SECURITY: Strip privileged fields - only admins can modify these
    PRIVILEGED_FIELDS = {"is_admin", "is_reviewer", "role"}
    if not requesting_user.is_admin:
        update_data = user_in.model_dump(exclude_unset=True)
        for field in PRIVILEGED_FIELDS:
            if field in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You cannot modify the '{field}' field"
                )
    
    return crud.update_user(db, user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> None:
    # Ownership check: users can only delete their own account (admins can delete anyone)
    requesting_user = crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    
    if x_user_id != user_id and not requesting_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
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


@router.get("/by-email/{email}", dependencies=[Depends(verify_admin)])
def get_user_id_by_email(email: str, db: Session = Depends(get_db)) -> dict:
    """Get user ID by email - admin only to prevent email enumeration"""
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
    
    print(f"BEFORE: user_id={user_id}, dates_logged_in={user.dates_logged_in}")
    
    dates = user.dates_logged_in or []
    
    if today in dates:
        return {"message": "Already logged in today", "date": today}
    
    user.dates_logged_in = dates + [today]
    print(f"AFTER ASSIGNMENT: dates_logged_in={user.dates_logged_in}")
    
    db.commit()
    
    db.refresh(user)
    print(f"AFTER COMMIT: dates_logged_in={user.dates_logged_in}")
    
    return {"message": "Login recorded", "date": today}


@router.get("/stats/logins", dependencies=[Depends(verify_admin)])
def get_login_stats(db: Session = Depends(get_db)) -> Dict[str, int]:
    start_date = date(2025, 10, 28)
    today = date.today()
    
    stats = {}
    current_date = start_date
    
    while current_date <= today:
        date_str = current_date.isoformat()
        count = db.query(User).filter(User.dates_logged_in.contains([date_str])).count()
        stats[date_str] = count
        current_date += timedelta(days=1)
    
    return stats


@router.get("/role/{role}", response_model=List[UserPublicRead])
def list_users_by_role(role: str, db: Session = Depends(get_db)) -> List[UserPublicRead]:
    """List all users with a specific role (e.g., 'author') - returns public info only"""
    users = db.query(User).filter(User.role == role).all()
    return list(users)


@router.post("/{user_id}/assign-author/{author_id}", response_model=UserRead)
def assign_author(
    user_id: str,
    author_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> UserRead:
    """
    Assign an author to a user.
    
    SECURITY: Ownership check - users can only assign authors to their own account.
    Without this, any authenticated user could modify anyone's author assignment (IDOR vulnerability).
    Admins can assign authors to any user.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    requesting_user = crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    
    # Ownership check: only the account owner OR an admin can assign authors
    if x_user_id != user_id and not requesting_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign authors to your own account"
        )
    
    author = crud.get_user(db, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if author.role != "author":
        raise HTTPException(status_code=400, detail="Selected user is not an author")
    
    user.assigned_author_id = author_id
    db.commit()
    db.refresh(user)
    return user
