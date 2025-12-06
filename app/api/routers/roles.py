from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth, verify_admin
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.crud import roles as crud

router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(verify_auth)])


@router.get("", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db)) -> List[RoleRead]:
    return list(crud.list_roles(db))


@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: str, db: Session = Depends(get_db)) -> RoleRead:
    role = crud.get_role(db, role_id)
    if not role:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)) -> RoleRead:
    return crud.create_role(db, role_in)


@router.patch("/{role_id}", response_model=RoleRead, dependencies=[Depends(verify_admin)])
def update_role(role_id: str, role_in: RoleUpdate, db: Session = Depends(get_db)) -> RoleRead:
    return crud.update_role(db, role_id, role_in)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin)])
def delete_role(role_id: str, db: Session = Depends(get_db)) -> None:
    crud.delete_role(db, role_id)
    return None


@router.post("/seed", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
def seed_roles(db: Session = Depends(get_db)) -> dict:
    created = crud.seed_default_roles(db)
    return {"message": f"Seeded {len(created)} roles", "roles": [r.role_id for r in created]}
