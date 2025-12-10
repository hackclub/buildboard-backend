import httpx
import logging
from sqlalchemy.orm import Session
from app.models.hackatime_project import HackatimeProject
from app.models.user import User
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def fetch_hackatime_stats(user_id: str, slack_id: str, db: Session) -> list[HackatimeProject]:
    """
    Fetches Hackatime stats for a user using the Admin API and updates the local database.
    """
    if not slack_id:
        logger.warning(f"User {user_id} has no slack_id, cannot fetch Hackatime stats")
        return []

    if not settings.HACKATIME_API_KEY:
        logger.warning("HACKATIME_API_KEY not configured, cannot fetch Hackatime stats")
        return []

    # Use the Admin API to get user projects
    url = f"{settings.HACKATIME_ADMIN_API_URL}/user/projects"
    params = {"id": slack_id}
    headers = {
        "Authorization": f"Bearer {settings.HACKATIME_API_KEY}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)

        if response.status_code != 200:
            logger.error(f"Failed to fetch Hackatime stats for {slack_id}: {response.status_code} {response.text}")
            return []

        projects_data = response.json()
        
        if not isinstance(projects_data, list):
            logger.warning(f"Hackatime API returned unexpected format for {slack_id}: {type(projects_data)}")
            return []

        # Process projects - aggregate by name
        aggregated_projects = {}
        for p in projects_data:
            name = p.get("name")
            if not name or name in ["<<LAST_PROJECT>>", "Other"]:
                continue

            # Admin API returns total_duration in seconds
            seconds = p.get("total_duration", 0)
            if name in aggregated_projects:
                aggregated_projects[name] += seconds
            else:
                aggregated_projects[name] = seconds

        # Upsert into DB
        updated_projects = []
        for name, seconds in aggregated_projects.items():
            existing = db.query(HackatimeProject).filter(
                HackatimeProject.user_id == user_id,
                HackatimeProject.name == name
            ).first()

            if existing:
                existing.seconds = seconds
                updated_projects.append(existing)
            else:
                new_project = HackatimeProject(
                    user_id=user_id,
                    name=name,
                    seconds=seconds
                )
                db.add(new_project)
                updated_projects.append(new_project)

        db.commit()

        # Return all current projects for the user
        return db.query(HackatimeProject).filter(HackatimeProject.user_id == user_id).all()

    except Exception as e:
        logger.error(f"Error fetching Hackatime stats for {user_id}: {e}")
        return []


async def lookup_hackatime_account_by_email(email: str) -> str | None:
    """
    Look up a Hackatime account ID by email address using the Admin API.
    Returns the Hackatime user ID if found, None otherwise.
    """
    if not settings.HACKATIME_API_KEY:
        logger.warning("HACKATIME_API_KEY not configured, cannot lookup Hackatime account")
        return None

    url = f"{settings.HACKATIME_ADMIN_API_URL}/execute"
    headers = {
        "Authorization": f"Bearer {settings.HACKATIME_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Query to find user by email
    payload = {
        "query": f"SELECT id FROM users WHERE email = '{email}' LIMIT 1"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)

        if response.status_code != 200:
            logger.error(f"Failed to lookup Hackatime account for {email}: {response.status_code}")
            return None

        data = response.json()
        if data and len(data) > 0 and "id" in data[0]:
            return data[0]["id"]
        
        return None

    except Exception as e:
        logger.error(f"Error looking up Hackatime account for {email}: {e}")
        return None
