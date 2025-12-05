"""
Seed script to add initial guides (Dhamari and Alex) to the database.
Run with: python seed_guides.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from app.db import SessionLocal, Base, engine
# Import all models to resolve relationships
from app.models.guide import Guide
from app.models.user import User
from app.models.project import Project
from app.models.vote import Vote
from app.models.review import Review
from app.models.hackatime_project import HackatimeProject

GUIDES = [
    {
        "guide_id": "guide-dhamari",
        "name": "Dhamari",
        "slack_id": "U08RWM5U4L9",
        "email": "dhamari@hackclub.com",
        "avatar_url": "/slides/female_char.png",
        "bio": None,
        "is_active": True
    },
    {
        "guide_id": "guide-alex",
        "name": "Alex",
        "slack_id": "U0823F39GV8",
        "email": "alexvd@hackclub.com",
        "avatar_url": "/slides/male_char.png",
        "bio": None,
        "is_active": True
    }
]


def seed_guides():
    db = SessionLocal()
    try:
        for guide_data in GUIDES:
            existing = db.query(Guide).filter(Guide.guide_id == guide_data["guide_id"]).first()
            if existing:
                print(f"Guide '{guide_data['name']}' already exists, updating...")
                for key, value in guide_data.items():
                    setattr(existing, key, value)
            else:
                print(f"Creating guide '{guide_data['name']}'...")
                guide = Guide(**guide_data)
                db.add(guide)
        
        db.commit()
        print("✅ Guides seeded successfully!")
        
        # List all guides
        guides = db.query(Guide).all()
        print(f"\nCurrent guides ({len(guides)}):")
        for g in guides:
            print(f"  - {g.name} ({g.email}) - Slack: {g.slack_id}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_guides()
