from fastapi import FastAPI
from app.api.routers.users import router as users_router
from app.api.routers.projects import router as projects_router
from app.api.routers.votes import router as votes_router
from app.db import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(votes_router)


@app.get("/")
def root():
    return {"message": "Accelerate Backend API"}
