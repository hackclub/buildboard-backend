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
from app.db import Base, engine, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.review import Review
from app.models.vote import Vote
from app.models.rsvp import RSVP
from sqlalchemy import and_
from app.migrate_db import run_migrations


async def airtable_sync_task():
    while True:
        try:
            db = SessionLocal()
            try:
                projects = db.query(Project).filter(
                    and_(
                        Project.sent_to_airtable == False,
                        Project.shipped == True,
                        Project.review_ids.isnot(None)
                    )
                ).all()
                
                filtered_projects = [p for p in projects if p.review_ids and len(p.review_ids) > 0]
                
                if filtered_projects:
                    print(f"\n📦 Found {len(filtered_projects)} project(s) to sync to Airtable:")
                    for project in filtered_projects:
                        print(f"  - {project.project_name} (ID: {project.project_id})")
            finally:
                db.close()
        except Exception as e:
            print(f"❌ Airtable sync error: {e}")
        
        await asyncio.sleep(10)


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

    task = asyncio.create_task(airtable_sync_task())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(projects_router)
app.include_router(votes_router)
app.include_router(reviews_router)
app.include_router(reviews_router)
app.include_router(rsvps_router)
app.include_router(hackatime_router)
app.include_router(github_router)
app.include_router(analytics_router)


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
