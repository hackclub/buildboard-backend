import logging
import os
from sqlalchemy import inspect
from alembic import command
from alembic.config import Config
from app.db import engine, Base

# Import models to ensure Base.metadata is populated
from app.models.user import User
from app.models.project import Project
from app.models.review import Review
from app.models.vote import Vote
from app.models.rsvp import RSVP
from app.models.hackatime_project import HackatimeProject
from app.models.onboarding_event import OnboardingEvent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_migrations():
    logger.info("Starting database migration check...")
    
    # Check if alembic.ini exists
    if not os.path.exists("alembic.ini"):
        logger.warning("alembic.ini not found. Skipping migrations.")
        return

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["is_auto_migration"] = True
    
    try:
        # 1. Ensure we are up to date with existing migrations
        logger.info("Running existing migrations...")
        command.upgrade(alembic_cfg, "head")
        
        # 2. Check for new changes and generate migration if needed
        logger.info("Checking for schema changes...")
        # We use a unique message for auto-generated migrations
        command.revision(alembic_cfg, message="auto_migration", autogenerate=True)
        
        # 3. Apply any new migrations (if generated)
        logger.info("Applying any new migrations...")
        command.upgrade(alembic_cfg, "head")
            
        logger.info("Migration process complete.")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        # We don't raise here to avoid preventing app startup if DB is temporarily down, 
        # though usually you want to fail fast.
        # For now, let's raise to be safe so we know if it fails.
        raise e
