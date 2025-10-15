from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    try:
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id or database constraint violation"
        )
    return project


def get_project(db: Session, project_id: str) -> Project | None:
    return db.get(Project, project_id)


def list_projects(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Project]:
    return db.query(Project).offset(skip).limit(limit).all()


def list_projects_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[Project]:
    return db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: str, data: ProjectUpdate) -> Project:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(project, k, v)
    
    try:
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database constraint violation"
        )
    return project


def delete_project(db: Session, project_id: str) -> None:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
