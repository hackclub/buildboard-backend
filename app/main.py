import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from app.api.routers.users import router as users_router
from app.api.routers.projects import router as projects_router
from app.api.routers.votes import router as votes_router
from app.api.routers.reviews import router as reviews_router
from app.api.routers.rsvps import router as rsvps_router
from app.api.routers.hackatime import router as hackatime_router
from app.api.routers.github import router as github_router
from app.api.routers.analytics import router as analytics_router
from app.api.routers.roles import router as roles_router
from app.db import Base, engine, SessionLocal
from app.models import User, Project, Review, Vote, RSVP
from sqlalchemy import and_
from app.migrate_db import run_migrations
from jobs.idv_sync import idv_sync_task
from jobs.airtable_sync import airtable_sync_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set start time when app starts
    app.state.start_time = datetime.now()
    
    # Run database migrations
    try:
        print("Running database migrations...")
        run_migrations()
        print("Database migrations completed.")
    except Exception as e:
        print(f"WARNING: Database migration failed: {e}")
        # We continue anyway, as it might be a transient DB issue or local dev setup
        pass

    airtable_task = asyncio.create_task(airtable_sync_task())
    idv_task = asyncio.create_task(idv_sync_task())
    yield
    airtable_task.cancel()
    idv_task.cancel()


app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(projects_router)
app.include_router(votes_router)
app.include_router(reviews_router)
app.include_router(rsvps_router)
app.include_router(hackatime_router)
app.include_router(github_router)
app.include_router(analytics_router)
app.include_router(utms_router)
app.include_router(roles_router)


@app.get("/")
def root():
    return {"message": "Bro - you lowkey shouldn't be here - go do something, there aren't any security flaws here for you to find"}


@app.get("/time")
def get_current_time():
    return {"current_time": datetime.now().isoformat()}


@app.get("/health")
def health_check():
    start_time = app.state.start_time
    uptime = datetime.now() - start_time
    return {
        "status": "up",
        "since": start_time.isoformat(),
        "uptime": str(uptime)
    }
