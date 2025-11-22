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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_migrations():
    logger.info("Starting database migration check...")
    
    # Check if alembic.ini exists
    if not os.path.exists("alembic.ini"):
        logger.warning("alembic.ini not found. Skipping migrations.")
        return

    alembic_cfg = Config("alembic.ini")
    
    try:
        inspector = inspect(engine)
        
        # Check if tables exist (we check 'users' as a proxy for the schema)
        has_users = inspector.has_table("users")
        
        if not has_users:
            logger.info("No 'users' table found. Creating all tables via SQLAlchemy...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created. Stamping database as head...")
            command.stamp(alembic_cfg, "head")
            logger.info("Database initialized and stamped.")
            return

        # Check if alembic_version table exists
        has_alembic_version = inspector.has_table("alembic_version")
        
        if has_alembic_version:
            logger.info("Alembic version table found. checking for pending migrations...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Migrations up to date.")
            return
            
        # Fallback: Tables exist but no alembic version. 
        # Check if we are in 'legacy' (old schema) or 'fresh-but-untracked' (new schema) state.
        # We check for a column that is new (e.g., is_idv in users)
        logger.info("Existing tables found but no alembic_version. Inspecting schema...")
        columns = [c["name"] for c in inspector.get_columns("users")]
        
        if "is_idv" in columns:
            logger.info("Tables appear to be up-to-date (is_idv present). Stamping as head...")
            command.stamp(alembic_cfg, "head")
        else:
            logger.info("Tables appear outdated (is_idv missing). Running migrations...")
            command.upgrade(alembic_cfg, "head")
            
        logger.info("Migration process complete.")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        # We don't raise here to avoid preventing app startup if DB is temporarily down, 
        # though usually you want to fail fast.
        # For now, let's raise to be safe so we know if it fails.
        raise e
