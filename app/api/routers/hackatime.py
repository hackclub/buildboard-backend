from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, verify_auth
from app.models.user import User
from app.schemas.hackatime import HackatimeProjectList, HackatimeProject
from app.services.hackatime import fetch_hackatime_stats
from app.core.config import get_settings

router = APIRouter(
    prefix="/hackatime",
    tags=["hackatime"],
    dependencies=[Depends(verify_auth)],
    responses={404: {"description": "Not found"}},
)

@router.post("/refresh", response_model=list[HackatimeProject])
async def refresh_hackatime_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refreshes Hackatime stats for the current user from the Hackatime API.
    """
    print(f"[Hackatime Router] /refresh called for user_id={current_user.user_id}, slack_id={current_user.slack_id}", flush=True)
    return await fetch_hackatime_stats(current_user.user_id, current_user.slack_id, db)

@router.get("/projects", response_model=list[HackatimeProject])
async def read_hackatime_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve Hackatime projects for the current user.
    Auto-fetches from Hackatime API if no projects exist in the database.
    """
    if not current_user.hackatime_projects:
        return await fetch_hackatime_stats(current_user.user_id, current_user.slack_id, db)
    return current_user.hackatime_projects


@router.get("/debug")
async def debug_hackatime(
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check hackatime configuration."""
    settings = get_settings()
    return {
        "user_id": current_user.user_id,
        "slack_id": current_user.slack_id,
        "has_api_key": bool(settings.HACKATIME_API_KEY),
        "api_key_length": len(settings.HACKATIME_API_KEY) if settings.HACKATIME_API_KEY else 0,
        "admin_api_url": settings.HACKATIME_ADMIN_API_URL,
        "existing_projects_count": len(current_user.hackatime_projects) if current_user.hackatime_projects else 0
    }
