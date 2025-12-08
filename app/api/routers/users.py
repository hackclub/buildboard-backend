from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, status, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, verify_auth, verify_admin
from app.schemas.user import (
    UserCreate, UserUpdate, UserPublicRead, UserSelfRead,
    UserProfileUpdate, UserAddressCreate, UserAddressUpdate,
    UserExistsResponse, LoginRecordedResponse, LinkIDVRequest
)
from app.schemas.project import ProjectRead
from app.crud import users as crud
from app.models.user import User
from app.models.user_login_event import UserLoginEvent

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(verify_auth)])


def _to_public_read(user: User) -> dict:
    """Convert user to public read format - strips all PII"""
    return {
        "user_id": user.user_id,
        "handle": user.handle,
        "profile": {
            "avatar_url": user.profile.avatar_url if user.profile else None,
            "bio": user.profile.bio if user.profile else None,
            "is_public": user.profile.is_public if user.profile else False,
        } if user.profile else None,
        "roles": [{"role_id": r.role_id} for r in user.roles] if user.roles else [],
        "created_at": user.created_at,
    }


def _to_self_read(user: User) -> dict:
    """Convert user to self read format - includes what user needs about themselves"""
    return {
        "user_id": user.user_id,
        "handle": user.handle,
        "referral_code": user.referral_code,
        "profile": {
            "avatar_url": user.profile.avatar_url if user.profile else None,
            "bio": user.profile.bio if user.profile else None,
            "is_public": user.profile.is_public if user.profile else False,
        } if user.profile else None,
        "roles": [{"role_id": r.role_id} for r in user.roles] if user.roles else [],
        "has_address": bool(user.addresses and len(user.addresses) > 0),
        "storyline_completed_at": user.storyline_completed_at.isoformat() if user.storyline_completed_at else None,
        "hackatime_completed_at": user.hackatime_completed_at.isoformat() if user.hackatime_completed_at else None,
        "slack_linked_at": user.slack_linked_at.isoformat() if user.slack_linked_at else None,
        "idv_completed_at": user.idv_completed_at.isoformat() if user.idv_completed_at else None,
        "onboarding_completed_at": user.onboarding_completed_at.isoformat() if user.onboarding_completed_at else None,
        "created_at": user.created_at,
    }


@router.post("", response_model=UserSelfRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> dict:
    user = crud.create_user(db, user_in)
    return _to_self_read(user)


@router.get("/by-email/{email}")
def get_user_id_by_email(email: str, db: Session = Depends(get_db)) -> dict:
    """Returns only user_id - no PII"""
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id}


@router.get("/by-identity-vault-id/{identity_vault_id}")
def get_user_by_identity_vault_id(identity_vault_id: str, db: Session = Depends(get_db)) -> dict:
    """Returns only user_id - no PII"""
    user = crud.get_user_by_identity_vault_id(db, identity_vault_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id}


@router.get("/stats/logins", dependencies=[Depends(verify_admin)])
def get_login_stats(db: Session = Depends(get_db)) -> dict:
    """Admin only - returns aggregate counts, no PII"""
    start_date = date(2025, 10, 28)
    today = date.today()

    stats = {}
    current_date = start_date

    while current_date <= today:
        date_str = current_date.isoformat()
        count = db.query(UserLoginEvent).filter(
            func.date(UserLoginEvent.logged_in_at) == current_date
        ).distinct(UserLoginEvent.user_id).count()
        stats[date_str] = count
        current_date += timedelta(days=1)

    return stats


@router.get("/{user_id}", response_model=UserSelfRead)
def get_user(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Get user - returns self read if requesting own data, public otherwise"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If requesting own data, return self view
    if x_user_id == user_id:
        return _to_self_read(user)
    
    # Otherwise return public view (if profile is public)
    if user.profile and user.profile.is_public:
        return _to_public_read(user)
    
    raise HTTPException(status_code=403, detail="Profile is private")


@router.get("", response_model=List[UserPublicRead], dependencies=[Depends(verify_admin)])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
) -> List[dict]:
    """Admin only - returns public info only"""
    users = crud.list_users(db, skip=skip, limit=limit)
    return [_to_public_read(u) for u in users]


@router.patch("/{user_id}", response_model=UserSelfRead)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Update user - only self can update"""
    if x_user_id != user_id:
        is_admin = crud.has_role(db, x_user_id, "admin")
        if not is_admin:
            raise HTTPException(status_code=403, detail="Can only update your own account")
    
    user = crud.update_user(db, user_id, user_in)
    return _to_self_read(user)


@router.patch("/{user_id}/profile", response_model=UserSelfRead)
def update_user_profile(
    user_id: str,
    profile_in: UserProfileUpdate,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Update profile - only self can update"""
    if x_user_id != user_id:
        is_admin = crud.has_role(db, x_user_id, "admin")
        if not is_admin:
            raise HTTPException(status_code=403, detail="Can only update your own profile")
    
    crud.update_user_profile(db, user_id, profile_in)
    user = crud.get_user(db, user_id)
    return _to_self_read(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
def delete_user(user_id: str, db: Session = Depends(get_db)) -> None:
    crud.delete_user(db, user_id)
    return None


@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
def add_user_role(user_id: str, role_id: str, db: Session = Depends(get_db)) -> dict:
    crud.add_user_role(db, user_id, role_id)
    return {"message": f"Role {role_id} added"}


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
def remove_user_role(user_id: str, role_id: str, db: Session = Depends(get_db)) -> None:
    crud.remove_user_role(db, user_id, role_id)
    return None


@router.get("/{user_id}/projects", response_model=List[ProjectRead])
def list_user_projects(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> List[ProjectRead]:
    """Get user's projects - only self or admin"""
    if x_user_id != user_id:
        is_admin = crud.has_role(db, x_user_id, "admin")
        if not is_admin:
            raise HTTPException(status_code=403, detail="Can only view your own projects")
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.projects


@router.get("/{user_id}/exists", response_model=UserExistsResponse)
def check_user_exists(user_id: str, db: Session = Depends(get_db)) -> UserExistsResponse:
    user = crud.get_user(db, user_id)
    return UserExistsResponse(exists=user is not None)


@router.post("/{user_id}/loggedin", response_model=LoginRecordedResponse)
def record_login(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> LoginRecordedResponse:
    """Record login - only self can record"""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only record your own login")
    
    login_event = crud.record_login(db, user_id)
    return LoginRecordedResponse(
        message="Login recorded",
        logged_in_at=login_event.logged_in_at.isoformat()
    )


@router.post("/{user_id}/addresses", status_code=status.HTTP_201_CREATED)
def create_user_address(
    user_id: str,
    address_in: UserAddressCreate,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Create address - only self can create. Returns success, not the address data."""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only add addresses to your own account")
    
    crud.create_user_address(db, user_id, address_in)
    return {"message": "Address added"}


@router.patch("/addresses/{address_id}")
def update_user_address(
    address_id: str,
    address_in: UserAddressUpdate,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Update address - only owner can update. Returns success, not the address data."""
    from app.models.user_address import UserAddress
    address = db.get(UserAddress, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    if address.user_id != x_user_id:
        raise HTTPException(status_code=403, detail="Can only update your own addresses")
    
    crud.update_user_address(db, address_id, address_in)
    return {"message": "Address updated"}


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_address(
    address_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> None:
    """Delete address - only owner can delete"""
    from app.models.user_address import UserAddress
    address = db.get(UserAddress, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    if address.user_id != x_user_id:
        raise HTTPException(status_code=403, detail="Can only delete your own addresses")
    
    crud.delete_user_address(db, address_id)
    return None


@router.post("/{user_id}/storyline-complete", response_model=UserSelfRead)
def complete_storyline(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Mark storyline as complete - only self can mark"""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only complete your own storyline")

    user = crud.complete_storyline(db, user_id)
    return _to_self_read(user)


@router.post("/{user_id}/hackatime-complete", response_model=UserSelfRead)
def complete_hackatime(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Mark hackatime setup as complete"""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only complete your own tasks")

    user = crud.complete_hackatime(db, user_id)
    return _to_self_read(user)


@router.post("/{user_id}/slack-complete", response_model=UserSelfRead)
def complete_slack_link(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Mark slack link as complete"""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only complete your own tasks")

    user = crud.complete_slack_link(db, user_id)
    return _to_self_read(user)


@router.post("/{user_id}/idv-complete", response_model=UserSelfRead)
def complete_idv(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Mark IDV as complete"""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only complete your own tasks")

    user = crud.complete_idv(db, user_id)
    return _to_self_read(user)


@router.post("/{user_id}/link-idv", response_model=UserSelfRead)
def link_idv(
    user_id: str,
    data: LinkIDVRequest,
    db: Session = Depends(get_db)
) -> dict:
    """Link identity vault to user account"""
    user = crud.link_idv(
        db,
        user_id,
        data.identity_vault_id,
        data.identity_vault_access_token,
        data.idv_country,
        data.verification_status,
        data.ysws_eligible
    )
    return _to_self_read(user)


@router.post("/{user_id}/onboarding-complete", response_model=UserSelfRead)
def complete_onboarding(
    user_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    """Mark onboarding as complete (all tasks done) - only self can mark"""
    if x_user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only complete your own onboarding")

    user = crud.complete_onboarding(db, user_id)
    return _to_self_read(user)
