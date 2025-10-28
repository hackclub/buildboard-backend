import requests
from dotenv import dotenv_values

dotenv = dotenv_values()
api_key = dotenv.get("MASTER_KEY")
user_id = input("Enter user ID: ")

url = f"http://localhost:8000/users/{user_id}/loggedin"
headers = {"Authorization": api_key}

response = requests.post(url, headers=headers)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.json()}")
