import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.routers.users import router as users_router
from app.api.routers.projects import router as projects_router
from app.api.routers.votes import router as votes_router
from app.api.routers.reviews import router as reviews_router
from app.db import Base, engine, SessionLocal
from app.models.project import Project
from app.models.user import User
from app.models.review import Review
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

load_dotenv()

try:
    from pyairtable import Api
    AIRTABLE_AVAILABLE = True
except ImportError:
    AIRTABLE_AVAILABLE = False
    print("⚠️  pyairtable not installed. Install with: pip install pyairtable")

def decide_github_username(code_url: str | None):
    if not code_url or len(code_url) == 0:
        return "N/A"
    elif "github.com" in code_url:
        parts = code_url.split("/")
        github_index = parts.index("github.com")
        if github_index + 1 <= len(parts):
            return parts[github_index + 1]
    return "N/A"

def get_hackatime_time_spent(project: Project) -> int:
    try:
        return int(project.time_spent or 0)
    except (TypeError, ValueError):
        return 0

def generate_justfification_text(project: Project) -> str:
    text = f"This project was submitted to Accelerate, and was likely built off of the Skeleton Code provided in Accelerate Week {project.submission_week}.\n\n"
    text += f"This project had {get_hackatime_time_spent(project)} hours logged in HackaTime.\n\n"

    reviewer_name = "N/A"
    justification = "N/A"
    try:
        if project.review_ids:
            db = SessionLocal()
            try:
                recent_review = (
                    db.query(Review)
                    .options(joinedload(Review.reviewer))
                    .filter(Review.review_id.in_(project.review_ids))
                    .order_by(Review.review_timestamp.desc())
                    .first()
                )
                if recent_review:
                    if recent_review.reviewer:
                        reviewer_name = f"{recent_review.reviewer.first_name} {recent_review.reviewer.last_name}"
                    else:
                        reviewer_user = (
                            db.query(User)
                            .filter(User.user_id == recent_review.reviewer_user_id)
                            .first()
                        )
                        if reviewer_user:
                            reviewer_name = f"{reviewer_user.first_name} {reviewer_user.last_name}"
                    justification = recent_review.review_comments or "N/A"
            finally:
                db.close()
    except Exception:
        pass

    text += f"This project went through review {len(project.review_ids) if project.review_ids else 0} time(s), and was most recently reviewed by {reviewer_name}.\n\n"
    text += f"They decided that this project should have its hours modified to {project.time_spent} hours.\n\n"
    text += f"The reason they gave for these hours is as follows: \n {justification} \n\n"
    text += f"This has also subsequently been batch spotchecked by AVD"
    return text

async def airtable_sync_task():
    while True:
        print("syncinnggggg")
        if not AIRTABLE_AVAILABLE:
            print(" Airtable sync disabled - pyairtable not installed")
            await asyncio.sleep(10)
            continue
        
        airtable_token = os.getenv("AIRTABLE_TOKEN")
        airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
        airtable_table_name = "YSWS Project Submission"
        
        if not airtable_token or not airtable_base_id:
            print("Airtable sync disabled - missing AIRTABLE_TOKEN or AIRTABLE_BASE_ID")
            await asyncio.sleep(10)
            continue
        
        api = Api(airtable_token)
        table = api.table(airtable_base_id, airtable_table_name)
        try:
            db = SessionLocal()
            try:
                projects = db.query(Project).filter(
                    and_(
                        Project.sent_to_airtable == False,
                        Project.shipped == True,
                        Project.review_ids.isnot(None),
                        Project.time_spent >= 0
                    )
                ).all()
                
                filtered_projects = [p for p in projects if p.review_ids and len(p.review_ids) > 0 and (p.time_spent) > 0]
                
                if filtered_projects:
                    print(f"\nFound {len(filtered_projects)} project(s) to sync to Airtable:")
                    for project in filtered_projects:
                        try:
                            user = db.query(User).filter(User.user_id == project.user_id).first()

                            screenshot_url = None
                            if project.attachment_urls and len(project.attachment_urls) > 0:
                                screenshot_url = project.attachment_urls[0]

                            reviewer_name = "N/A"
                            recent_review = None
                            if project.review_ids:
                                recent_review = (
                                    db.query(Review)
                                    .options(joinedload(Review.reviewer))
                                    .filter(Review.review_id.in_(project.review_ids))
                                    .order_by(Review.review_timestamp.desc())
                                    .first()
                                )
                            if recent_review and recent_review.reviewer:
                                reviewer_name = f"{recent_review.reviewer.first_name} {recent_review.reviewer.last_name}"
                            elif recent_review:
                                reviewer_user = (
                                    db.query(User)
                                    .filter(User.user_id == recent_review.reviewer_user_id)
                                    .first()
                                )
                                if reviewer_user:
                                    reviewer_name = f"{reviewer_user.first_name} {reviewer_user.last_name}"

                            record_data = {
                                "Code URL": project.code_url,
                                "Playable URL": project.live_url,
                                "How did you hear about this?": "N/A",
                                "What are we doing well?": "N/A",
                                "How can we improve?": "N/A",
                                "First Name": user.first_name if user else "John",
                                "Last Name": user.last_name if user else "Doe",
                                "Email": user.email if user else "johdoe@hackclub.com",
                                "Screenshot": screenshot_url,
                                "Description": project.project_description,
                                "Github Username": decide_github_username(project.code_url),
                                "Address (Line 1)": user.address_line_1 if user else "Error",
                                "Address (Line 2)": user.address_line_2 if user else "Error",
                                "City": user.city if user else "Error",
                                "State / Province": user.state if user else "Error",
                                "Country": user.country if user else "Error",
                                "Zip / Postal Code": user.post_code if user else "Error",
                                "Optional - Override Hours Spent": project.time_spent,
                                "Optional - Override Hours Spent Justification": generate_justfification_text(project),
                                "Reviewer": reviewer_name,
                            }
                            
                            table.create(record_data)
                            project.sent_to_airtable = True
                            db.commit()
                            print(f" Syncie: {project.project_name} (drivers licence: {project.project_id})")
                        except Exception as e:
                            print(f"Oppps {project.project_name}: {e}")
                            db.rollback()
            finally:
                db.close()
        except Exception as e:
            print(f"Airtable sync error: {e} Idk how you let this happen. be better, fix it.")
        
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
