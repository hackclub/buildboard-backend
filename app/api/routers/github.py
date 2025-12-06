from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.user import User
from app.crud import users as users_crud
from app.services.github_service import GitHubService

router = APIRouter()
github_service = GitHubService()

class GitHubLinkRequest(BaseModel):
    installation_id: str
    repo_path: str

class ReadmeUpdateRequest(BaseModel):
    content: str
    sha: str | None = None
    message: str = "Update README via Buildboard"

@router.post("/projects/{project_id}/github/link")
def link_github_repo(
    project_id: str,
    request: GitHubLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_admin = users_crud.has_role(db, current_user.user_id, "admin")
    if project.user_id != current_user.user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to edit this project")

    project.github_installation_id = request.installation_id
    project.github_repo_path = request.repo_path
    db.commit()

    return {"status": "success", "message": "GitHub repository linked"}

@router.get("/projects/{project_id}/readme")
def get_project_readme(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.github_installation_id or not project.github_repo_path:
        raise HTTPException(status_code=400, detail="GitHub repository not linked")

    try:
        readme_data = github_service.get_readme(project.github_installation_id, project.github_repo_path)
        return readme_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}/readme")
def update_project_readme(
    project_id: str,
    request: ReadmeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_admin = users_crud.has_role(db, current_user.user_id, "admin")
    if project.user_id != current_user.user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to edit this project")

    if not project.github_installation_id or not project.github_repo_path:
        raise HTTPException(status_code=400, detail="GitHub repository not linked")

    try:
        result = github_service.update_readme(
            project.github_installation_id,
            project.github_repo_path,
            request.content,
            request.sha,
            request.message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
