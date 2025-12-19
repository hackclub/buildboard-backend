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
    logger.info(f"[Hackatime] fetch_hackatime_stats called for user_id={user_id}, slack_id={slack_id}")
    
    if not slack_id:
        logger.warning(f"[Hackatime] User {user_id} has no slack_id, cannot fetch Hackatime stats")
        return []

    if not settings.HACKATIME_API_KEY:
        logger.warning("[Hackatime] HACKATIME_API_KEY not configured, cannot fetch Hackatime stats")
        return []
    
    logger.info(f"[Hackatime] API key present, length={len(settings.HACKATIME_API_KEY)}")

    # First, look up the Hackatime internal user ID from the slack_uid
    hackatime_user_id = await lookup_hackatime_user_id_by_slack(slack_id)
    if not hackatime_user_id:
        logger.warning(f"[Hackatime] Could not find Hackatime user for slack_id {slack_id}")
        return []
    
    logger.info(f"[Hackatime] Found Hackatime user_id={hackatime_user_id} for slack_id={slack_id}")

    # Use the Admin API to get user projects
    url = f"{settings.HACKATIME_ADMIN_API_URL}/user/projects"
    params = {"id": hackatime_user_id}
    headers = {
        "Authorization": f"Bearer {settings.HACKATIME_API_KEY}"
    }

    try:
        logger.info(f"[Hackatime] Fetching projects from {url} for hackatime_user_id={hackatime_user_id}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)

        logger.info(f"[Hackatime] Projects API response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"[Hackatime] Failed to fetch stats for {slack_id}: {response.status_code} {response.text[:200]}")
            return []

        response_data = response.json()
        
        # Handle the response format: {"user_id": ..., "username": ..., "projects": [...]}
        if isinstance(response_data, dict) and "projects" in response_data:
            projects_data = response_data["projects"]
        elif isinstance(response_data, list):
            projects_data = response_data
        else:
            logger.warning(f"Hackatime API returned unexpected format for {slack_id}: {type(response_data)}")
            return []

        logger.info(f"[Hackatime] Received {len(projects_data)} projects from API")
        
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
        
        all_projects = db.query(HackatimeProject).filter(HackatimeProject.user_id == user_id).all()
        logger.info(f"[Hackatime] Saved {len(aggregated_projects)} unique projects, total in DB: {len(all_projects)}")

        # Return all current projects for the user
        return all_projects

    except Exception as e:
        logger.error(f"[Hackatime] Error fetching stats for {user_id}: {e}", exc_info=True)
        return []


async def lookup_hackatime_user_id_by_slack(slack_id: str) -> int | None:
    """
    Look up a Hackatime internal user ID by Slack ID using the Admin API.
    Returns the Hackatime user ID if found, None otherwise.
    """
    logger.info(f"[Hackatime] Looking up Hackatime user for slack_id={slack_id}")
    
    if not settings.HACKATIME_API_KEY:
        logger.warning("[Hackatime] HACKATIME_API_KEY not configured, cannot lookup Hackatime user")
        return None

    url = f"{settings.HACKATIME_ADMIN_API_URL}/execute"
    headers = {
        "Authorization": f"Bearer {settings.HACKATIME_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": f"SELECT id FROM users WHERE slack_uid = '{slack_id}' LIMIT 1"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)

        logger.info(f"[Hackatime] Lookup response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"[Hackatime] Failed to lookup user for slack_id {slack_id}: {response.status_code} {response.text[:200]}")
            return None

        data = response.json()
        logger.info(f"[Hackatime] Lookup response: success={data.get('success')}, rows={len(data.get('rows', []))}")
        if data.get("success") and data.get("rows") and len(data["rows"]) > 0:
            # Extract the ID from the response format: {"id": ["id", 17636]}
            id_value = data["rows"][0].get("id")
            if isinstance(id_value, list) and len(id_value) > 1:
                return id_value[1]
            elif isinstance(id_value, int):
                return id_value
        
        return None

    except Exception as e:
        logger.error(f"Error looking up Hackatime user for slack_id {slack_id}: {e}")
        return None


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
