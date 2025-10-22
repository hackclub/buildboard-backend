import requests, dotenv
import json
from datetime import datetime

dotenv.load_dotenv()

BASE_URL = dotenv.get_key("BASE_URL") or "http://localhost:45000"
API_KEY = dotenv.get_key("TEST_API_KEY")
HEADERS = {"api-key": API_KEY}

def create_test_user():
    print("\n📝 Creating test user...")
    user_data = {
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "slack_id": input("Slack ID: "),
        "email": input("Email: "),
        "is_admin": input("Is admin? (y/n): ").lower() == 'y'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users", headers=HEADERS, json=user_data)
        if response.status_code == 201:
            print("\n✅ User created successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")

def view_users():
    print("\n👥 Fetching all users...")
    
    try:
        response = requests.get(f"{BASE_URL}/users", headers=HEADERS)
        if response.status_code == 200:
            users = response.json()
            print(f"\n📊 Found {len(users)} user(s):\n")
            for user in users:
                print(f"ID: {user['user_id']}")
                print(f"Name: {user['first_name']} {user['last_name']}")
                print(f"Email: {user['email']}")
                print(f"Slack ID: {user['slack_id']}")
                print(f"Admin: {user['is_admin']}")
                print(f"Created: {user['created_at']}")
                print("-" * 60)
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")

def delete_all_users():
    print("\n⚠️  WARNING: This will delete ALL users!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("❌ Cancelled")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/users", headers=HEADERS)
        if response.status_code == 200:
            users = response.json()
            print(f"\n🗑️  Deleting {len(users)} user(s)...")
            
            deleted = 0
            for user in users:
                delete_response = requests.delete(
                    f"{BASE_URL}/users/{user['user_id']}", 
                    headers=HEADERS
                )
                if delete_response.status_code == 204:
                    deleted += 1
                    print(f"✅ Deleted: {user['first_name']} {user['last_name']}")
                else:
                    print(f"❌ Failed to delete: {user['user_id']}")
            
            print(f"\n✅ Deleted {deleted}/{len(users)} users")
        else:
            print(f"\n❌ Error fetching users: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    while True:
        print("\n" + "="*60)
        print("👤 USER MANAGEMENT")
        print("="*60)
        print("1. Create test user")
        print("2. View all users")
        print("3. Delete all users")
        print("4. Exit")
        print("="*60)
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            create_test_user()
        elif choice == "2":
            view_users()
        elif choice == "3":
            delete_all_users()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    print("\n🚀 User Management Script")
    print(f"API: {BASE_URL}")
    main()
