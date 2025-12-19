import asyncio
import sys
sys.path.insert(0, '.')

from app.db import SessionLocal
from app.models.user import User
from app.services.hackatime import fetch_hackatime_stats, lookup_hackatime_user_id_by_slack

async def test():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "dhamaritricehanson@gmail.com").first()
    
    print(f"User ID: {user.user_id}")
    print(f"Slack ID: {user.slack_id}")
    
    # Test lookup
    hackatime_id = await lookup_hackatime_user_id_by_slack(user.slack_id)
    print(f"Hackatime User ID: {hackatime_id}")
    
    # Test full fetch
    projects = await fetch_hackatime_stats(user.user_id, user.slack_id, db)
    print(f"Projects: {len(projects)}")
    for p in projects[:5]:
        print(f"  - {p.name}: {p.seconds}s")
    
    db.close()

asyncio.run(test())
