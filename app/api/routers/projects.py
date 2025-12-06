from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException, Header
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.crud import projects as crud
from app.crud import users as users_crud

router = APIRouter(prefix="/projects", tags=["projects"], dependencies=[Depends(verify_auth)])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    return crud.create_project(db, project_in)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db)) -> ProjectRead:
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=List[ProjectRead])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: str | None = Query(None),
    db: Session = Depends(get_db)
) -> List[ProjectRead]:
    if user_id:
        return list(crud.list_projects_by_user(db, user_id, skip=skip, limit=limit))
    return list(crud.list_projects(db, skip=skip, limit=limit))


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> ProjectRead:
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    requesting_user = users_crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")

    is_admin = users_crud.has_role(db, x_user_id, "admin")
    if project.user_id != x_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own projects"
        )

    return crud.update_project(db, project_id, project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> None:
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    requesting_user = users_crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")

    is_admin = users_crud.has_role(db, x_user_id, "admin")
    if project.user_id != x_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own projects"
        )

    crud.delete_project(db, project_id)
    return None


@router.post("/{project_id}/hackatime/{hackatime_project_id}", status_code=status.HTTP_201_CREATED)
def link_hackatime_project(
    project_id: str,
    hackatime_project_id: str,
    db: Session = Depends(get_db)
) -> dict:
    crud.link_hackatime_project(db, project_id, hackatime_project_id)
    return {"message": "Hackatime project linked"}


@router.delete("/{project_id}/hackatime/{hackatime_project_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_hackatime_project(
    project_id: str,
    hackatime_project_id: str,
    db: Session = Depends(get_db)
) -> None:
    crud.unlink_hackatime_project(db, project_id, hackatime_project_id)
    return None
