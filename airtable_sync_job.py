from app.db import SessionLocal
from app.models.project import Project
from sqlalchemy import and_


def find_projects_to_sync():
    db = SessionLocal()
    
    try:
        print("🔍 Searching for projects to sync to Airtable...\n")
        
        projects = db.query(Project).filter(
            and_(
                Project.sent_to_airtable == False,
                Project.shipped == True,
                Project.review_ids.isnot(None)
            )
        ).all()
        
        filtered_projects = [p for p in projects if p.review_ids and len(p.review_ids) > 0]
        
        if not filtered_projects:
            print("✅ No projects found matching criteria")
            return
        
        print(f"📦 Found {len(filtered_projects)} project(s) to sync:\n")
        print("=" * 80)
        
        for project in filtered_projects:
            print(f"\nProject ID: {project.project_id}")
            print(f"Name: {project.project_name}")
            print(f"Description: {project.project_description[:100]}..." if len(project.project_description) > 100 else f"Description: {project.project_description}")
            print(f"User ID: {project.user_id}")
            print(f"Submission Week: {project.submission_week}")
            print(f"Code URL: {project.code_url}")
            print(f"Live URL: {project.live_url}")
            print(f"Review IDs: {project.review_ids}")
            print(f"Shipped: {project.shipped}")
            print(f"Sent to Airtable: {project.sent_to_airtable}")
            print(f"Created At: {project.created_at}")
            print("-" * 80)
        
        print(f"\n✅ Total projects ready for Airtable sync: {len(filtered_projects)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Airtable Sync Background Job\n")
    find_projects_to_sync()
