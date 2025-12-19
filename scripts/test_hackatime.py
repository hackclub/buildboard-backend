import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

HACKATIME_API_KEY = os.getenv("HACKATIME_API_KEY")
HACKATIME_ADMIN_API_URL = "https://hackatime.hackclub.com/api/admin/v1"
HACKATIME_USER_ID = 13126

async def test_projects():
    print(f"Testing Hackatime projects for user ID: {HACKATIME_USER_ID}")
    
    url = f"{HACKATIME_ADMIN_API_URL}/user/projects"
    params = {"id": HACKATIME_USER_ID}
    headers = {
        "Authorization": f"Bearer {HACKATIME_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=10.0)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")

asyncio.run(test_projects())
