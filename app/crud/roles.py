from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


def create_role(db: Session, data: RoleCreate) -> Role:
    role = Role(**data.model_dump())
    db.add(role)
    try:
        db.commit()
        db.refresh(role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists"
        )
    return role


def get_role(db: Session, role_id: str) -> Role | None:
    return db.get(Role, role_id)


def list_roles(db: Session) -> Sequence[Role]:
    return db.query(Role).all()


def update_role(db: Session, role_id: str, data: RoleUpdate) -> Role:
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(role, k, v)

    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: str) -> None:
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()


def seed_default_roles(db: Session) -> list[Role]:
    """Seed the default roles if they don't exist."""
    default_roles = [
        {"role_id": "admin", "name": "Administrator", "description": "Full system access"},
        {"role_id": "reviewer", "name": "Reviewer", "description": "Can review projects"},
        {"role_id": "idv", "name": "IDV", "description": "Identity verified"},
        {"role_id": "slack_member", "name": "Slack Member", "description": "Member of Slack workspace"},
    ]

    created = []
    for role_data in default_roles:
        existing = db.get(Role, role_data["role_id"])
        if not existing:
            role = Role(**role_data)
            db.add(role)
            created.append(role)

    if created:
        db.commit()
        for role in created:
            db.refresh(role)

    return created
