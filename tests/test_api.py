import requests, dotenv
import json
from datetime import datetime
#sa
dotenv.load_dotenv()

BASE_URL = dotenv.get_key("BASE_URL") or "http://localhost:45000"
API_KEY = dotenv.get_key("TEST_API_KEY")
HEADERS = {"api-key": API_KEY}

def print_response(endpoint, method, response):
    print(f"\n{'='*80}")
    print(f"{method} {endpoint}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print('='*80)

def test_root():
    print("\n🧪 Testing Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response("/", "GET", response)

def test_users():
    print("\n🧪 Testing Users Endpoints")
    
    # Create user
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "slack_id": f"U{datetime.now().timestamp()}",
        "email": f"test{int(datetime.now().timestamp())}@example.com",
        "is_admin": False
    }
    response = requests.post(f"{BASE_URL}/users", headers=HEADERS, json=user_data)
    print_response("/users", "POST", response)
    
    if response.status_code == 201:
        user_id = response.json()["user_id"]
        
        # Get user
        response = requests.get(f"{BASE_URL}/users/{user_id}", headers=HEADERS)
        print_response(f"/users/{user_id}", "GET", response)
        
        # Update user
        update_data = {"first_name": "Updated"}
        response = requests.patch(f"{BASE_URL}/users/{user_id}", headers=HEADERS, json=update_data)
        print_response(f"/users/{user_id}", "PATCH", response)
        
        # List users
        response = requests.get(f"{BASE_URL}/users", headers=HEADERS)
        print_response("/users", "GET", response)
        
        # Delete user
        response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=HEADERS)
        print_response(f"/users/{user_id}", "DELETE", response)

def test_projects():
    print("\n🧪 Testing Projects Endpoints")
    
    # Create user for project
    user_data = {
        "first_name": "Project",
        "last_name": "Owner",
        "slack_id": f"U{datetime.now().timestamp()}",
        "email": f"owner{int(datetime.now().timestamp())}@example.com",
        "is_admin": False
    }
    user_response = requests.post(f"{BASE_URL}/users", headers=HEADERS, json=user_data)
    
    if user_response.status_code == 201:
        user_id = user_response.json()["user_id"]
        
        # Create project
        project_data = {
            "project_name": "Test Project",
            "project_description": "This is a test project",
            "user_id": user_id,
            "submission_week": 1,
            "shipped": False
        }
        response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json=project_data)
        print_response("/projects", "POST", response)
        
        if response.status_code == 201:
            project_id = response.json()["project_id"]
            
            # Get project
            response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
            print_response(f"/projects/{project_id}", "GET", response)
            
            # Update project
            update_data = {"shipped": True}
            response = requests.patch(f"{BASE_URL}/projects/{project_id}", headers=HEADERS, json=update_data)
            print_response(f"/projects/{project_id}", "PATCH", response)
            
            # List projects
            response = requests.get(f"{BASE_URL}/projects", headers=HEADERS)
            print_response("/projects", "GET", response)
            
            # List projects by user
            response = requests.get(f"{BASE_URL}/projects?user_id={user_id}", headers=HEADERS)
            print_response(f"/projects?user_id={user_id}", "GET", response)
            
            # Delete project
            response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
            print_response(f"/projects/{project_id}", "DELETE", response)
        
        # Cleanup user
        requests.delete(f"{BASE_URL}/users/{user_id}", headers=HEADERS)

def test_votes():
    print("\n🧪 Testing Votes Endpoints")
    
    # Create user and project for vote
    user_data = {
        "first_name": "Voter",
        "last_name": "User",
        "slack_id": f"U{datetime.now().timestamp()}",
        "email": f"voter{int(datetime.now().timestamp())}@example.com",
        "is_admin": False
    }
    user_response = requests.post(f"{BASE_URL}/users", headers=HEADERS, json=user_data)
    
    if user_response.status_code == 201:
        user_id = user_response.json()["user_id"]
        
        project_data = {
            "project_name": "Vote Test Project",
            "project_description": "Project for testing votes",
            "user_id": user_id,
            "submission_week": 1,
            "shipped": False
        }
        project_response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json=project_data)
        
        if project_response.status_code == 201:
            project_id = project_response.json()["project_id"]
            
            # Create vote
            vote_data = {
                "user_id": user_id,
                "project_id": project_id,
                "vote_ranking": 5
            }
            response = requests.post(f"{BASE_URL}/votes", headers=HEADERS, json=vote_data)
            print_response("/votes", "POST", response)
            
            if response.status_code == 201:
                vote_id = response.json()["vote_id"]
                
                # Get vote
                response = requests.get(f"{BASE_URL}/votes/{vote_id}", headers=HEADERS)
                print_response(f"/votes/{vote_id}", "GET", response)
                
                # Update vote
                update_data = {"vote_ranking": 10}
                response = requests.patch(f"{BASE_URL}/votes/{vote_id}", headers=HEADERS, json=update_data)
                print_response(f"/votes/{vote_id}", "PATCH", response)
                
                # List votes
                response = requests.get(f"{BASE_URL}/votes", headers=HEADERS)
                print_response("/votes", "GET", response)
                
                # List votes by project
                response = requests.get(f"{BASE_URL}/votes?project_id={project_id}", headers=HEADERS)
                print_response(f"/votes?project_id={project_id}", "GET", response)
                
                # List votes by user
                response = requests.get(f"{BASE_URL}/votes?user_id={user_id}", headers=HEADERS)
                print_response(f"/votes?user_id={user_id}", "GET", response)
                
                # Delete vote
                response = requests.delete(f"{BASE_URL}/votes/{vote_id}", headers=HEADERS)
                print_response(f"/votes/{vote_id}", "DELETE", response)
            
            # Cleanup
            requests.delete(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
        
        requests.delete(f"{BASE_URL}/users/{user_id}", headers=HEADERS)

def test_reviews():
    print("\n🧪 Testing Reviews Endpoints (Requires Admin)")
    
    # Create admin user and project
    admin_data = {
        "first_name": "Admin",
        "last_name": "Reviewer",
        "slack_id": f"U{datetime.now().timestamp()}",
        "email": f"admin{int(datetime.now().timestamp())}@example.com",
        "is_admin": True
    }
    admin_response = requests.post(f"{BASE_URL}/users", headers=HEADERS, json=admin_data)
    
    if admin_response.status_code == 201:
        admin_id = admin_response.json()["user_id"]
        
        project_data = {
            "project_name": "Review Test Project",
            "project_description": "Project for testing reviews",
            "user_id": admin_id,
            "submission_week": 1,
            "shipped": False
        }
        project_response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json=project_data)
        
        if project_response.status_code == 201:
            project_id = project_response.json()["project_id"]
            
            # Create review (requires admin)
            review_headers = {**HEADERS, "x-user-id": admin_id}
            review_data = {
                "reviewer_user_id": admin_id,
                "project_id": project_id,
                "review_comments": "This is a test review",
                "review_decision": "approved"
            }
            response = requests.post(f"{BASE_URL}/reviews", headers=review_headers, json=review_data)
            print_response("/reviews", "POST", response)
            
            if response.status_code == 201:
                review_id = response.json()["review_id"]
                
                # Get review
                response = requests.get(f"{BASE_URL}/reviews/{review_id}", headers=HEADERS)
                print_response(f"/reviews/{review_id}", "GET", response)
                
                # Update review
                update_data = {"review_decision": "rejected"}
                response = requests.patch(f"{BASE_URL}/reviews/{review_id}", headers=HEADERS, json=update_data)
                print_response(f"/reviews/{review_id}", "PATCH", response)
                
                # List reviews
                response = requests.get(f"{BASE_URL}/reviews", headers=HEADERS)
                print_response("/reviews", "GET", response)
                
                # List reviews by project
                response = requests.get(f"{BASE_URL}/reviews?project_id={project_id}", headers=HEADERS)
                print_response(f"/reviews?project_id={project_id}", "GET", response)
                
                # List reviews by reviewer
                response = requests.get(f"{BASE_URL}/reviews?reviewer_user_id={admin_id}", headers=HEADERS)
                print_response(f"/reviews?reviewer_user_id={admin_id}", "GET", response)
                
                # Delete review
                response = requests.delete(f"{BASE_URL}/reviews/{review_id}", headers=HEADERS)
                print_response(f"/reviews/{review_id}", "DELETE", response)
            
            # Cleanup
            requests.delete(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
        
        requests.delete(f"{BASE_URL}/users/{admin_id}", headers=HEADERS)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Starting API Tests")
    print(f"Base URL: {BASE_URL}")
    print("="*80)
    
    try:
        test_root()
        test_users()
        test_projects()
        test_votes()
        test_reviews()
        
        print("\n" + "="*80)
        print("✅ All tests completed!")
        print("="*80)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
