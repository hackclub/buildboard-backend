import sys
import os

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.hackatime_project import HackatimeProject
from app.models.vote import Vote
from app.models.review import Review
from app.models.rsvp import RSVP
from app.utils.handle_generator import generate_friendly_handle

def fix_null_handles():
    db: Session = SessionLocal()
    try:
        users = db.query(User).filter(User.handle == None).all()
        print(f"Found {len(users)} users with null handles.")
        
        for user in users:
            new_handle = generate_friendly_handle()
            print(f"Assigning handle {new_handle} to user {user.user_id}")
            user.handle = new_handle
            
        db.commit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_null_handles()
