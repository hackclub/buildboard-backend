from app.db import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()

print(f"\n📋 Found {len(users)} user(s):\n")
for u in users:
    email = u.email
    slack_id = u.slack_id or "None"
    print(f"  Email: {email} | Slack ID: {slack_id}")

db.close()
