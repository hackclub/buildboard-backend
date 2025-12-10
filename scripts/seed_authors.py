"""
Seed script to set Dhamari and Alex as authors.
Run with: python seed_authors.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from app.db import SessionLocal, Base, engine
from app.models.user import User
from app.models.project import Project
from app.models.vote import Vote
from app.models.review import Review
from app.models.hackatime_project import HackatimeProject

AUTHORS = [
    {
        "email": "dhamari@hackclub.com",
        "first_name": "Dhamari",
        "last_name": "BuildBoard",
        "slack_id": "U08RWM5U4L9",
        "role": "author",
        "avatar_url": "/slides/female_char.png"
    },
    {
        "email": "alexvd@hackclub.com",
        "first_name": "Alex",
        "last_name": "BuildBoard",
        "slack_id": "U0823F39GV8",
        "role": "author",
        "avatar_url": "/slides/male_char.png"
    }
]


def seed_authors():
    db = SessionLocal()
    try:
        for author_data in AUTHORS:
            existing = db.query(User).filter(User.email == author_data["email"]).first()
            if existing:
                print(f"User '{author_data['first_name']}' exists, updating to author...")
                existing.role = author_data["role"]
                existing.avatar_url = author_data["avatar_url"]
                if not existing.slack_id:
                    existing.slack_id = author_data["slack_id"]
            else:
                print(f"Creating author '{author_data['first_name']}'...")
                user = User(**author_data)
                db.add(user)
        
        db.commit()
        print("✅ Authors seeded successfully!")
        
        # List all authors
        authors = db.query(User).filter(User.role == "author").all()
        print(f"\nCurrent authors ({len(authors)}):")
        for a in authors:
            print(f"  - {a.first_name} {a.last_name} ({a.email}) - Slack: {a.slack_id}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_authors()
