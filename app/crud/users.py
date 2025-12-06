from typing import Sequence
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_address import UserAddress
from app.models.user_role import UserRole
from app.models.user_login_event import UserLoginEvent
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate, UserAddressCreate, UserAddressUpdate
from app.utils.handle_generator import generate_friendly_handle


def create_user(db: Session, data: UserCreate) -> User:
    user_data = data.model_dump(exclude={"profile", "address"})
    if not user_data.get("handle"):
        user_data["handle"] = generate_friendly_handle()

    user = User(**user_data)
    db.add(user)

    profile = UserProfile(user_id=user.user_id, **data.profile.model_dump())
    db.add(profile)

    if data.address:
        address = UserAddress(user_id=user.user_id, **data.address.model_dump())
        db.add(address)

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
    return db.query(User).options(
        joinedload(User.profile),
        joinedload(User.addresses),
        joinedload(User.roles).joinedload(UserRole.role)
    ).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).options(
        joinedload(User.profile),
        joinedload(User.addresses),
        joinedload(User.roles).joinedload(UserRole.role)
    ).filter(User.email == email.lower()).first()


def get_user_by_handle(db: Session, handle: str) -> User | None:
    return db.query(User).options(
        joinedload(User.profile),
        joinedload(User.addresses),
        joinedload(User.roles).joinedload(UserRole.role)
    ).filter(User.handle == handle).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> Sequence[User]:
    return db.query(User).options(
        joinedload(User.profile),
        joinedload(User.roles).joinedload(UserRole.role)
    ).offset(skip).limit(limit).all()


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


def update_user_profile(db: Session, user_id: str, data: UserProfileUpdate) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    return profile


def create_user_address(db: Session, user_id: str, data: UserAddressCreate) -> UserAddress:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.is_primary:
        db.query(UserAddress).filter(
            UserAddress.user_id == user_id,
            UserAddress.is_primary == True
        ).update({"is_primary": False})

    address = UserAddress(user_id=user_id, **data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def update_user_address(db: Session, address_id: str, data: UserAddressUpdate) -> UserAddress:
    address = db.get(UserAddress, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if data.is_primary:
        db.query(UserAddress).filter(
            UserAddress.user_id == address.user_id,
            UserAddress.is_primary == True,
            UserAddress.id != address_id
        ).update({"is_primary": False})

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(address, k, v)

    db.commit()
    db.refresh(address)
    return address


def delete_user_address(db: Session, address_id: str) -> None:
    address = db.get(UserAddress, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()


def delete_user(db: Session, user_id: str) -> None:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


def add_user_role(db: Session, user_id: str, role_id: str) -> UserRole:
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    if existing:
        return existing

    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role


def remove_user_role(db: Session, user_id: str, role_id: str) -> None:
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    if user_role:
        db.delete(user_role)
        db.commit()


def has_role(db: Session, user_id: str, role_id: str) -> bool:
    return db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first() is not None


def record_login(db: Session, user_id: str) -> UserLoginEvent:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    login_event = UserLoginEvent(user_id=user_id)
    db.add(login_event)
    db.commit()
    db.refresh(login_event)
    return login_event


def get_login_events(db: Session, user_id: str, limit: int = 100) -> Sequence[UserLoginEvent]:
    return db.query(UserLoginEvent).filter(
        UserLoginEvent.user_id == user_id
    ).order_by(UserLoginEvent.logged_in_at.desc()).limit(limit).all()
