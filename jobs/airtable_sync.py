"""
Airtable Sync Job

Periodically checks for shipped projects with reviews that haven't been synced to Airtable.
"""

import os
import asyncio
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from app.db import SessionLocal
from app.models.project import Project


AIRTABLE_SYNC_INTERVAL_SECONDS = int(os.getenv("AIRTABLE_SYNC_INTERVAL_SECONDS", "10"))


def run_airtable_sync():
    """Main sync function."""
    db = SessionLocal()
    
    try:
        projects = db.query(Project).options(
            joinedload(Project.reviews)
        ).filter(
            and_(
                Project.sent_to_airtable == False,
                Project.shipped == True
            )
        ).all()

        filtered_projects = [p for p in projects if p.reviews and len(p.reviews) > 0]

        if filtered_projects:
            print(f"\n📦 [Airtable Sync] Found {len(filtered_projects)} project(s) to sync:")
            for project in filtered_projects:
                print(f"  - {project.project_name} (ID: {project.project_id})")
        
    except Exception as e:
        print(f"❌ [Airtable Sync] Error: {e}")
    finally:
        db.close()


async def airtable_sync_task():
    """Background task that runs Airtable sync periodically."""
    while True:
        try:
            run_airtable_sync()
        except Exception as e:
            print(f"❌ [Airtable Sync] Task error: {e}")
        
        await asyncio.sleep(AIRTABLE_SYNC_INTERVAL_SECONDS)
