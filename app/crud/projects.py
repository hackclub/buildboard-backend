from typing import Sequence
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.project import Project
from app.models.project_hackatime_link import ProjectHackatimeLink
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, data: ProjectCreate) -> Project:
    project_data = data.model_dump(exclude={"hackatime_project_ids"})
    project = Project(**project_data)
    db.add(project)

    if data.hackatime_project_ids:
        for hackatime_id in data.hackatime_project_ids:
            link = ProjectHackatimeLink(
                project_id=project.project_id,
                hackatime_project_id=hackatime_id
            )
            db.add(link)

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
    return db.query(Project).options(
        joinedload(Project.hackatime_links)
    ).filter(Project.project_id == project_id).first()


def list_projects(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Project]:
    return db.query(Project).options(
        joinedload(Project.hackatime_links)
    ).offset(skip).limit(limit).all()


def list_projects_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[Project]:
    return db.query(Project).options(
        joinedload(Project.hackatime_links)
    ).filter(Project.user_id == user_id).offset(skip).limit(limit).all()


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
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()


def link_hackatime_project(db: Session, project_id: str, hackatime_project_id: str) -> ProjectHackatimeLink:
    existing = db.query(ProjectHackatimeLink).filter(
        ProjectHackatimeLink.project_id == project_id,
        ProjectHackatimeLink.hackatime_project_id == hackatime_project_id
    ).first()
    if existing:
        return existing

    link = ProjectHackatimeLink(
        project_id=project_id,
        hackatime_project_id=hackatime_project_id
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def unlink_hackatime_project(db: Session, project_id: str, hackatime_project_id: str) -> None:
    link = db.query(ProjectHackatimeLink).filter(
        ProjectHackatimeLink.project_id == project_id,
        ProjectHackatimeLink.hackatime_project_id == hackatime_project_id
    ).first()
    if link:
        db.delete(link)
        db.commit()
