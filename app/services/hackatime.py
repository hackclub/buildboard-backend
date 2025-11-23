import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.hackatime_project import HackatimeProject
from app.models.user import User

logger = logging.getLogger(__name__)

async def fetch_hackatime_stats(user_id: str, slack_id: str, db: Session) -> list[HackatimeProject]:
    """
    Fetches Hackatime stats for a user and updates the local database.
    """
    if not slack_id:
        logger.warning(f"User {user_id} has no slack_id, cannot fetch Hackatime stats")
        return []

    # Calculate start date (e.g., from beginning of event or a reasonable lookback)
    # Using the date from the reference code: 2025-06-16, but let's use a more generic one or config
    # For now, let's default to a fixed date or just recent history if not specified.
    # The reference code used 2025-06-16. Let's use a hardcoded date for now as per reference.
    start_date = "2025-06-16T00:00:00Z" 
    
    url = f"https://hackatime.hackclub.com/api/v1/users/{slack_id}/stats"
    params = {
        "features": "projects",
        "start_date": start_date,
        "test_param": "true"
    }

    # TODO: Add HACKATIME_BYPASS_KEYS if needed from env
    headers = {} 
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            
        if response.status_code != 200:
            logger.error(f"Failed to fetch Hackatime stats for {slack_id}: {response.status_code} {response.text}")
            return []

        data = response.json()
        if data.get("data", {}).get("status") != "ok":
             logger.warning(f"Hackatime API returned non-ok status for {slack_id}")
             return []
             
        projects_data = data.get("data", {}).get("projects", [])
        
        # Process projects
        # We need to aggregate by name because the API might return multiple entries? 
        # Reference code did aggregation.
        
        aggregated_projects = {}
        for p in projects_data:
            name = p.get("name")
            if not name or name in ["<<LAST_PROJECT>>", "Other"]:
                continue
                
            seconds = p.get("total_seconds", 0)
            if name in aggregated_projects:
                aggregated_projects[name] += seconds
            else:
                aggregated_projects[name] = seconds

        # Upsert into DB
        # Since we are using SQLite (likely) or Postgres, we need to handle upsert carefully.
        # Buildboard seems to use Postgres based on the schema file (pg_catalog).
        # But let's check if we can use standard SQLAlchemy merge or specific dialect.
        # The reference used upsert_all.
        
        updated_projects = []
        for name, seconds in aggregated_projects.items():
            # Check if exists
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
