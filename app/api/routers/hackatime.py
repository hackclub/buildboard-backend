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
    """Debug endpoint to check hackatime configuration and test API."""
    import httpx
    
    settings = get_settings()
    result = {
        "user_id": current_user.user_id,
        "slack_id": current_user.slack_id,
        "has_api_key": bool(settings.HACKATIME_API_KEY),
        "api_key_length": len(settings.HACKATIME_API_KEY) if settings.HACKATIME_API_KEY else 0,
        "admin_api_url": settings.HACKATIME_ADMIN_API_URL,
        "existing_projects_count": len(current_user.hackatime_projects) if current_user.hackatime_projects else 0
    }
    
    # Try to look up the Hackatime user ID
    if current_user.slack_id and settings.HACKATIME_API_KEY:
        try:
            url = f"{settings.HACKATIME_ADMIN_API_URL}/execute"
            headers = {
                "Authorization": f"Bearer {settings.HACKATIME_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": f"SELECT id FROM users WHERE slack_uid = '{current_user.slack_id}' LIMIT 1"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                
                result["lookup_status"] = response.status_code
                result["lookup_response"] = response.json() if response.status_code == 200 else response.text[:500]
                
                # If we got a user ID, try to fetch their projects
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("rows") and len(data["rows"]) > 0:
                        id_value = data["rows"][0].get("id")
                        if isinstance(id_value, list) and len(id_value) > 1:
                            hackatime_user_id = id_value[1]
                        elif isinstance(id_value, int):
                            hackatime_user_id = id_value
                        else:
                            hackatime_user_id = None
                        
                        result["hackatime_user_id"] = hackatime_user_id
                        
                        if hackatime_user_id:
                            # Fetch projects
                            projects_url = f"{settings.HACKATIME_ADMIN_API_URL}/user/projects"
                            projects_response = await client.get(
                                projects_url,
                                params={"id": hackatime_user_id},
                                headers={"Authorization": f"Bearer {settings.HACKATIME_API_KEY}"},
                                timeout=10.0
                            )
                            result["projects_status"] = projects_response.status_code
                            if projects_response.status_code == 200:
                                projects_data = projects_response.json()
                                if isinstance(projects_data, dict) and "projects" in projects_data:
                                    result["projects_count"] = len(projects_data["projects"])
                                    result["sample_projects"] = [p.get("name") for p in projects_data["projects"][:5]]
                                elif isinstance(projects_data, list):
                                    result["projects_count"] = len(projects_data)
                                    result["sample_projects"] = [p.get("name") for p in projects_data[:5]]
                            else:
                                result["projects_error"] = projects_response.text[:500]
        except Exception as e:
            result["error"] = str(e)
    
    return result
