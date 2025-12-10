from app.db import SessionLocal, Base, engine
from app.models.user import User
from app.models.project import Project
from app.models.vote import Vote
from app.models.review import Review
from uuid import uuid4

def seed_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding database with mock data...")
        
        users_data = [
            {"first_name": "Alice", "last_name": "Johnson", "slack_id": "U001ALICE", "email": "alice@hackclub.com", "is_admin": False},
            {"first_name": "Bob", "last_name": "Smith", "slack_id": "U002BOBSM", "email": "bob@hackclub.com", "is_admin": False},
            {"first_name": "Charlie", "last_name": "Brown", "slack_id": "U003CHARL", "email": "charlie@hackclub.com", "is_admin": False},
            {"first_name": "Diana", "last_name": "Prince", "slack_id": "U004DIANA", "email": "diana@hackclub.com", "is_admin": True},
            {"first_name": "Eve", "last_name": "Martinez", "slack_id": "U005EVEMA", "email": "eve@hackclub.com", "is_admin": True},
        ]
        
        users = []
        for user_data in users_data:
            user = User(user_id=str(uuid4()), **user_data)
            db.add(user)
            users.append(user)
        
        db.commit()
        print(f"Created {len(users)} users")
        
        projects_data = [
            {
                "user_id": users[0].user_id,
                "project_name": "AI Chat Bot",
                "project_description": "Built an AI-powered chat bot using GPT-4 that helps students with homework questions.",
                "attachment_urls": ["https://example.com/screenshot1.png", "https://example.com/demo.gif"],
                "code_url": "https://github.com/alice/ai-chatbot",
                "live_url": "https://ai-chatbot-demo.vercel.app",
                "submission_week": 1,
                "paper_url": None,
                "time_spent": 240
            },
            {
                "user_id": users[0].user_id,
                "project_name": "Weather Dashboard",
                "project_description": "A real-time weather dashboard with beautiful visualizations and alerts.",
                "attachment_urls": ["https://example.com/weather-ss.png"],
                "code_url": "https://github.com/alice/weather-dash",
                "live_url": "https://weather-dash.netlify.app",
                "submission_week": 2,
                "paper_url": None,
                "time_spent": 180
            },
            {
                "user_id": users[1].user_id,
                "project_name": "Task Manager Pro",
                "project_description": "A productivity app with Kanban boards, time tracking, and team collaboration features.",
                "attachment_urls": ["https://example.com/taskmanager1.png", "https://example.com/taskmanager2.png"],
                "code_url": "https://github.com/bob/taskmanager",
                "live_url": "https://taskmanager-pro.app",
                "submission_week": 1,
                "paper_url": None,
                "time_spent": 360
            },
            {
                "user_id": users[2].user_id,
                "project_name": "Blockchain Explorer",
                "project_description": "A web app to explore blockchain transactions with detailed analytics and visualizations.",
                "attachment_urls": None,
                "code_url": "https://github.com/charlie/blockchain-explorer",
                "live_url": "https://block-explorer.io",
                "submission_week": 1,
                "paper_url": "https://example.com/blockchain-paper.pdf",
                "time_spent": 480
            },
            {
                "user_id": users[2].user_id,
                "project_name": "Recipe Finder",
                "project_description": "Find recipes based on ingredients you have at home. Uses ML for recommendations.",
                "attachment_urls": ["https://example.com/recipe1.png"],
                "code_url": "https://github.com/charlie/recipe-finder",
                "live_url": "https://recipe-finder.app",
                "submission_week": 2,
                "paper_url": None,
                "time_spent": 120
            },
            {
                "user_id": users[3].user_id,
                "project_name": "Fitness Tracker",
                "project_description": "Track your workouts, nutrition, and progress with detailed analytics and graphs.",
                "attachment_urls": ["https://example.com/fitness1.png", "https://example.com/fitness2.png", "https://example.com/fitness3.png"],
                "code_url": "https://github.com/diana/fitness-tracker",
                "live_url": "https://fitness-track.app",
                "submission_week": 1,
                "paper_url": None,
                "time_spent": 300
            },
            {
                "user_id": users[4].user_id,
                "project_name": "Music Visualizer",
                "project_description": "Real-time audio visualization with WebGL. Creates stunning visuals that react to music.",
                "attachment_urls": ["https://example.com/music-viz.gif"],
                "code_url": "https://github.com/eve/music-visualizer",
                "live_url": "https://music-viz.app",
                "submission_week": 2,
                "paper_url": None,
                "time_spent": 200
            },
        ]
        
        projects = []
        for project_data in projects_data:
            project = Project(project_id=str(uuid4()), **project_data)
            db.add(project)
            projects.append(project)
        
        db.commit()
        print(f"Created {len(projects)} projects")
        
        votes_data = [
            {"user_id": users[1].user_id, "project_id": projects[0].project_id, "vote_ranking": 1},
            {"user_id": users[2].user_id, "project_id": projects[0].project_id, "vote_ranking": 2},
            {"user_id": users[3].user_id, "project_id": projects[0].project_id, "vote_ranking": 1},
            {"user_id": users[4].user_id, "project_id": projects[0].project_id, "vote_ranking": 3},
            
            {"user_id": users[0].user_id, "project_id": projects[2].project_id, "vote_ranking": 1},
            {"user_id": users[2].user_id, "project_id": projects[2].project_id, "vote_ranking": 1},
            {"user_id": users[3].user_id, "project_id": projects[2].project_id, "vote_ranking": 2},
            
            {"user_id": users[0].user_id, "project_id": projects[3].project_id, "vote_ranking": 2},
            {"user_id": users[1].user_id, "project_id": projects[3].project_id, "vote_ranking": 1},
            {"user_id": users[4].user_id, "project_id": projects[3].project_id, "vote_ranking": 1},
            
            {"user_id": users[0].user_id, "project_id": projects[5].project_id, "vote_ranking": 3},
            {"user_id": users[1].user_id, "project_id": projects[5].project_id, "vote_ranking": 2},
            {"user_id": users[2].user_id, "project_id": projects[5].project_id, "vote_ranking": 1},
            
            {"user_id": users[3].user_id, "project_id": projects[6].project_id, "vote_ranking": 1},
            {"user_id": users[4].user_id, "project_id": projects[6].project_id, "vote_ranking": 2},
        ]
        
        votes = []
        for vote_data in votes_data:
            vote = Vote(vote_id=str(uuid4()), **vote_data)
            db.add(vote)
            votes.append(vote)
        
        db.commit()
        print(f"Created {len(votes)} votes")
        
        reviews_data = [
            {
                "reviewer_user_id": users[3].user_id,
                "project_id": projects[0].project_id,
                "review_comments": "Great implementation! The AI responses are accurate and the UI is intuitive. Would love to see more customization options.",
                "review_decision": "Approved"
            },
            {
                "reviewer_user_id": users[4].user_id,
                "project_id": projects[0].project_id,
                "review_comments": "Impressive work with GPT-4 integration. Consider adding rate limiting for production use.",
                "review_decision": "Approved"
            },
            {
                "reviewer_user_id": users[2].user_id,
                "project_id": projects[2].project_id,
                "review_comments": "Solid productivity app. The Kanban board is well-designed. Minor issues with the time tracking feature.",
                "review_decision": "Needs Revision"
            },
            {
                "reviewer_user_id": users[0].user_id,
                "project_id": projects[3].project_id,
                "review_comments": "Excellent blockchain visualization. The analytics dashboard is particularly impressive. Great documentation too!",
                "review_decision": "Approved"
            },
            {
                "reviewer_user_id": users[1].user_id,
                "project_id": projects[5].project_id,
                "review_comments": "Nice fitness tracking features. The graphs are clear and helpful. Would benefit from social features.",
                "review_decision": "Approved"
            },
        ]
        
        reviews = []
        for review_data in reviews_data:
            review = Review(review_id=str(uuid4()), **review_data)
            db.add(review)
            reviews.append(review)
        
        db.commit()
        print(f"Created {len(reviews)} reviews")
        
        print("\n✅ Database seeded successfully!")
        print(f"   Users: {len(users)}")
        print(f"   Projects: {len(projects)}")
        print(f"   Votes: {len(votes)}")
        print(f"   Reviews: {len(reviews)}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
