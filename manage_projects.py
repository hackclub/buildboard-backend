import requests, dotenv
import json
from datetime import datetime

dotenv.load_dotenv()

BASE_URL = "https://y08gko88kskgs08kcc80c040.a.selfhosted.hackclub.com/"
API_KEY = "themasterofkeys"
HEADERS = {"api-key": API_KEY}

def create_test_project():
    print("\n📝 Creating test project...")
    
    user_id = input("User ID: ")
    project_data = {
        "user_id": user_id,
        "project_name": input("Project name: "),
        "project_description": input("Project description: "),
        "code_url": input("Code URL (optional): ") or None,
        "live_url": input("Live URL (optional): ") or None,
        "submission_week": int(input("Submission week: ")),
        "shipped": input("Shipped? (y/n): ").lower() == 'y',
        "sent_to_airtable": input("Sent to Airtable? (y/n): ").lower() == 'y'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json=project_data)
        if response.status_code == 201:
            print("\n✅ Project created successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")

def view_projects():
    print("\n📦 Fetching all projects...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=HEADERS)
        if response.status_code == 200:
            projects = response.json()
            print(f"\n📊 Found {len(projects)} project(s):\n")
            for project in projects:
                print(f"ID: {project['project_id']}")
                print(f"Name: {project['project_name']}")
                print(f"Description: {project['project_description'][:80]}..." if len(project['project_description']) > 80 else f"Description: {project['project_description']}")
                print(f"User ID: {project['user_id']}")
                print(f"Week: {project['submission_week']}")
                print(f"Code URL: {project.get('code_url', 'N/A')}")
                print(f"Live URL: {project.get('live_url', 'N/A')}")
                print(f"Shipped: {project['shipped']}")
                print(f"Sent to Airtable: {project['sent_to_airtable']}")
                print(f"Review IDs: {project.get('review_ids', [])}")
                print(f"Created: {project['created_at']}")
                print("-" * 60)
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")

def view_project_by_id():
    print("\n🔍 View project by ID...")
    project_id = input("Project ID: ")
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
        if response.status_code == 200:
            project = response.json()
            print("\n✅ Project found:")
            print(json.dumps(project, indent=2))
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")

def update_project():
    print("\n✏️  Update project...")
    project_id = input("Project ID: ")
    
    print("\nLeave blank to keep existing value:")
    update_data = {}
    
    project_name = input("New project name (optional): ")
    if project_name:
        update_data["project_name"] = project_name
    
    shipped = input("Shipped? (y/n/blank): ").strip().lower()
    if shipped:
        update_data["shipped"] = shipped == 'y'
    
    sent_to_airtable = input("Sent to Airtable? (y/n/blank): ").strip().lower()
    if sent_to_airtable:
        update_data["sent_to_airtable"] = sent_to_airtable == 'y'
    
    if not update_data:
        print("❌ No updates provided")
        return
    
    try:
        response = requests.patch(f"{BASE_URL}/projects/{project_id}", headers=HEADERS, json=update_data)
        if response.status_code == 200:
            print("\n✅ Project updated successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")

def delete_all_projects():
    print("\n⚠️  WARNING: This will delete ALL projects!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("❌ Cancelled")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=HEADERS)
        if response.status_code == 200:
            projects = response.json()
            print(f"\n🗑️  Deleting {len(projects)} project(s)...")
            
            deleted = 0
            for project in projects:
                delete_response = requests.delete(
                    f"{BASE_URL}/projects/{project['project_id']}", 
                    headers=HEADERS
                )
                if delete_response.status_code == 204:
                    deleted += 1
                    print(f"✅ Deleted: {project['project_name']}")
                else:
                    print(f"❌ Failed to delete: {project['project_id']}")
            
            print(f"\n✅ Deleted {deleted}/{len(projects)} projects")
        else:
            print(f"\n❌ Error fetching projects: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    while True:
        print("\n" + "="*60)
        print("📦 PROJECT MANAGEMENT")
        print("="*60)
        print("1. Create test project")
        print("2. View all projects")
        print("3. View project by ID")
        print("4. Update project")
        print("5. Delete all projects")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            create_test_project()
        elif choice == "2":
            view_projects()
        elif choice == "3":
            view_project_by_id()
        elif choice == "4":
            update_project()
        elif choice == "5":
            delete_all_projects()
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    print("\n🚀 Project Management Script")
    print(f"API: {BASE_URL}")
    main()
