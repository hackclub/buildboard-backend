from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.hackatime import HackatimeProjectList, HackatimeProject
from app.services.hackatime import fetch_hackatime_stats

router = APIRouter(
    prefix="/hackatime",
    tags=["hackatime"],
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
    return await fetch_hackatime_stats(current_user.user_id, current_user.slack_id, db)

@router.get("/projects", response_model=list[HackatimeProject])
def read_hackatime_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve Hackatime projects for the current user.
    """
    return current_user.hackatime_projects
