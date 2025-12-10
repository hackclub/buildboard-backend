from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.project import Project
from app.models.hackatime_project import HackatimeProject
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, data: ProjectCreate) -> Project:
    project_data = data.model_dump()
    project = Project(**project_data)
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
    return db.query(Project).filter(Project.project_id == project_id).first()


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
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()


def update_hackatime_projects(
    db: Session,
    project_id: str,
    user_id: str,
    project_names: list[str]
) -> Project:
    """
    Update hackatime projects for a project (like midnight does).
    - Validates ownership
    - Checks for conflicts (same hackatime project can't be in multiple user projects)
    - Calculates hours from linked hackatime projects
    """
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own projects"
        )
    
    if not project_names:
        project.hackatime_projects = []
        project.hackatime_hours = None
        db.commit()
        db.refresh(project)
        return project
    
    # Get all user's OTHER projects to check for conflicts
    other_projects = db.query(Project).filter(
        Project.user_id == user_id,
        Project.project_id != project_id
    ).all()
    
    # Build set of project names already linked to other projects
    linked_by_others = set()
    for other_project in other_projects:
        if other_project.hackatime_projects:
            for name in other_project.hackatime_projects:
                linked_by_others.add(name)
    
    # Check for conflicts
    conflicts = [name for name in project_names if name in linked_by_others]
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"These hackatime projects are already linked to another project: {', '.join(conflicts)}"
        )
    
    # Get user's hackatime projects to validate names and calculate hours
    hackatime_projects = db.query(HackatimeProject).filter(
        HackatimeProject.user_id == user_id,
        HackatimeProject.name.in_(project_names)
    ).all()
    
    # Build map of name -> seconds
    projects_map = {hp.name: hp.seconds for hp in hackatime_projects}
    
    # Validate all requested projects exist
    for name in project_names:
        if name not in projects_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hackatime project '{name}' not found. Please refresh your hackatime stats first."
            )
    
    # Calculate total hours
    total_seconds = sum(projects_map[name] for name in project_names)
    total_hours = total_seconds / 3600.0
    
    # Update project
    project.hackatime_projects = project_names
    project.hackatime_hours = round(total_hours, 2)
    
    db.commit()
    db.refresh(project)
    return project


def get_unlinked_hackatime_projects(db: Session, user_id: str) -> list[HackatimeProject]:
    """
    Get hackatime projects NOT yet linked to any of the user's projects.
    """
    # Get all hackatime projects for user
    all_hackatime = db.query(HackatimeProject).filter(
        HackatimeProject.user_id == user_id
    ).all()
    
    # Get all linked project names across all user's projects
    user_projects = db.query(Project).filter(Project.user_id == user_id).all()
    linked_names = set()
    for project in user_projects:
        if project.hackatime_projects:
            for name in project.hackatime_projects:
                linked_names.add(name)
    
    # Filter out already linked ones
    return [hp for hp in all_hackatime if hp.name not in linked_names]


def get_linked_hackatime_projects(db: Session, user_id: str, project_id: str) -> list[HackatimeProject]:
    """
    Get hackatime projects linked to a specific project.
    """
    project = get_project(db, project_id)
    if not project or project.user_id != user_id:
        return []
    
    if not project.hackatime_projects:
        return []
    
    # Get the actual hackatime project objects
    return db.query(HackatimeProject).filter(
        HackatimeProject.user_id == user_id,
        HackatimeProject.name.in_(project.hackatime_projects)
    ).all()
