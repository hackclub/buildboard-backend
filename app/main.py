import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from app.api.routers.users import router as users_router
from app.api.routers.projects import router as projects_router
from app.api.routers.votes import router as votes_router
from app.api.routers.reviews import router as reviews_router
from app.db import Base, engine, SessionLocal
from app.models.project import Project
from sqlalchemy import and_


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
    task = asyncio.create_task(airtable_sync_task())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(votes_router)
app.include_router(reviews_router)


@app.get("/")
def root():
    return {"message": "Bro - you lowkey shouldn't be here - go do something, there aren't any security flaws here for you to find"}


@app.get("/time")
def get_current_time():
    return {"current_time": datetime.now().isoformat()}
