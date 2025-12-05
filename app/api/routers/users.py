from typing import List, Dict
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth, verify_admin
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.project import ProjectRead
from app.crud import users as crud
from app.models.user import User
from app.services.referral import generate_qr_code, generate_referral_link
from app.core.utm import UTMCampaign
from app.services.poster import generate_referral_poster

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


@router.get("/stats/logins")
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


@router.get("/{user_id}/referral/qr")
def get_referral_qr_code(user_id: str, db: Session = Depends(get_db)) -> Response:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    qr_bytes = generate_qr_code(user.referral_code)
    return Response(content=qr_bytes, media_type="image/png")


@router.get("/{user_id}/referral/link")
def get_user_referral_link(
    user_id: str,
    campaign: UTMCampaign | None = None,
    db: Session = Depends(get_db),
) -> dict:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "referral_code": user.referral_code,
        "referral_link": generate_referral_link(user.referral_code, campaign),
    }


@router.get("/{user_id}/referral/poster")
def get_referral_poster(user_id: str, db: Session = Depends(get_db)) -> Response:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_name = f"{user.first_name} {user.last_name}"
    poster_bytes = generate_referral_poster(user.referral_code, user_name)
    return Response(content=poster_bytes, media_type="image/png")
