import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from db import Base, get_db
from models.user import User
from models.task import Task, Submission

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "display_name": "Test User"
    }

@pytest.fixture
def admin_user():
    return {
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "display_name": "Admin User"
    }

@pytest.fixture
def auth_headers(client: TestClient, test_user, setup_test_db):
    """Create authenticated user and return headers"""
    # Register user
    client.post("/api/auth/register", json=test_user)
    
    # Login user
    login_response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    access_token = login_response.json()["data"]["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(client: TestClient, admin_user, setup_test_db):
    """Create authenticated admin and return headers"""
    # Register admin
    client.post("/api/auth/register", json=admin_user)
    
    # Login admin
    login_response = client.post("/api/auth/login", json={
        "email": admin_user["email"],
        "password": admin_user["password"]
    })
    access_token = login_response.json()["data"]["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def sample_task():
    return {
        "title": "Test Task",
        "description": "Complete this test task to earn XP",
        "xp_reward": 25,
        "proof_type": "text",
        "priority": "medium",
        "category": "learning"
    }

class TestTasks:
    """Test tasks endpoints"""
    
    def test_get_tasks_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting tasks list"""
        response = client.get("/api/tasks", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tasks" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "limit" in data["data"]
    
    def test_get_tasks_with_filters(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting tasks with filters"""
        # Create tasks with different properties
        tasks_data = [
            {"title": "High Priority Task", "description": "High priority", "xp_reward": 30, "priority": "high"},
            {"title": "Low Priority Task", "description": "Low priority", "xp_reward": 15, "priority": "low"},
            {"title": "Image Task", "description": "Requires image proof", "xp_reward": 20, "proof_type": "image"},
            {"title": "Link Task", "description": "Requires link proof", "xp_reward": 25, "proof_type": "link"}
        ]
        
        # Create tasks as admin
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        for task_data in tasks_data:
            client.post("/api/tasks", json=task_data, headers=admin_headers)
        
        # Test filters
        response = client.get("/api/tasks?priority=high", headers=auth_headers)
        data = response.json()
        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["priority"] == "high"
        
        response = client.get("/api/tasks?proof_type=image", headers=auth_headers)
        data = response.json()
        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["proof_type"] == "image"
    
    def test_get_task_by_id_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting a specific task"""
        # Create a task first
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        task_data = {"title": "Test Task", "description": "Test description", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        # Get the task
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == task_id
        assert data["data"]["title"] == task_data["title"]
    
    def test_get_task_not_found(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting a non-existent task"""
        response = client.get("/api/tasks/99999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_create_task_success(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating a task"""
        task_data = {
            "title": "New Task",
            "description": "Complete this task to earn XP",
            "xp_reward": 30,
            "proof_type": "text",
            "priority": "medium",
            "category": "learning"
        }
        
        response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["title"] == task_data["title"]
        assert data["data"]["xp_reward"] == task_data["xp_reward"]
    
    def test_create_task_unauthorized(self, client: TestClient, auth_headers, setup_test_db):
        """Test creating a task without admin rights"""
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "xp_reward": 30
        }
        
        response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
    
    def test_create_task_with_deadline(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating a task with deadline"""
        future_deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Task with Deadline",
            "description": "Complete before deadline",
            "xp_reward": 40,
            "deadline": future_deadline
        }
        
        response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["deadline"] == future_deadline

class TestSubmissions:
    """Test task submissions"""
    
    def test_claim_task_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test claiming a task"""
        # Create a task first
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        task_data = {"title": "Claimable Task", "description": "Task to claim", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        # Claim the task
        response = client.post(f"/api/tasks/{task_id}/claim", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["claimed"] is True
    
    def test_claim_already_claimed_task(self, client: TestClient, auth_headers, setup_test_db):
        """Test claiming an already claimed task"""
        # Create a task and claim it once
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        task_data = {"title": "Claimable Task", "description": "Task to claim", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        client.post(f"/api/tasks/{task_id}/claim", headers=auth_headers)
        
        # Try to claim again
        response = client.post(f"/api/tasks/{task_id}/claim", headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
    
    def test_submit_task_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test submitting a task"""
        # Create and claim a task
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        task_data = {"title": "Submittable Task", "description": "Task to submit", "xp_reward": 25, "proof_type": "text"}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        client.post(f"/api/tasks/{task_id}/claim", headers=auth_headers)
        
        # Submit the task
        submission_data = {
            "proof": "I have completed this task successfully. Here is the proof of my work."
        }
        response = client.post(f"/api/tasks/{task_id}/submit", json=submission_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["proof"] == submission_data["proof"]
        assert data["data"]["status"] == "pending"
    
    def test_submit_task_with_media(self, client: TestClient, auth_headers, setup_test_db):
        """Test submitting a task with media proof"""
        # Create and claim a task with image proof type
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        task_data = {"title": "Image Task", "description": "Task with image proof", "xp_reward": 30, "proof_type": "image"}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        client.post(f"/api/tasks/{task_id}/claim", headers=auth_headers)
        
        # Submit with image URL
        submission_data = {
            "proof": "Task completed with image proof",
            "proof_url": "https://example.com/task-proof.jpg"
        }
        response = client.post(f"/api/tasks/{task_id}/submit", json=submission_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["proof_url"] == submission_data["proof_url"]
    
    def test_submit_unclaimed_task(self, client: TestClient, auth_headers, setup_test_db):
        """Test submitting a task without claiming it first"""
        # Create a task
        admin_user = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_user)
        admin_login = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        task_data = {"title": "Direct Submit Task", "description": "Task to submit directly", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        # Try to submit without claiming
        submission_data = {"proof": "Direct submission"}
        response = client.post(f"/api/tasks/{task_id}/submit", json=submission_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
    
    def test_get_user_submissions(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting user's submissions"""
        response = client.get("/api/tasks/submissions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "submissions" in data["data"]
    
    def test_get_task_submissions(self, client: TestClient, admin_headers, setup_test_db):
        """Test getting submissions for a specific task"""
        # Create a task
        task_data = {"title": "Task with Submissions", "description": "Task to get submissions for", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        # Create some submissions
        users = [
            {"email": "user1@example.com", "password": "Password123!", "display_name": "User 1"},
            {"email": "user2@example.com", "password": "Password123!", "display_name": "User 2"}
        ]
        
        for user_data in users:
            client.post("/api/auth/register", json=user_data)
            login = client.post("/api/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
            token = login.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            client.post(f"/api/tasks/{task_id}/claim", headers=headers)
            client.post(f"/api/tasks/{task_id}/submit", json={"proof": f"Submission by {user_data['display_name']}"}, headers=headers)
        
        # Get submissions for the task
        response = client.get(f"/api/tasks/{task_id}/submissions", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2

class TestTaskModeration:
    """Test task moderation"""
    
    def test_admin_approve_submission(self, client: TestClient, admin_headers, setup_test_db):
        """Test admin approving a submission"""
        # Create a task and submission
        task_data = {"title": "Moderatable Task", "description": "Task to moderate", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        # Create user and submit
        user_data = {"email": "submitter@example.com", "password": "Password123!", "display_name": "Submitter"}
        client.post("/api/auth/register", json=user_data)
        login = client.post("/api/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
        token = login.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post(f"/api/tasks/{task_id}/claim", headers=headers)
        submit_response = client.post(f"/api/tasks/{task_id}/submit", json={"proof": "Task completed"}, headers=headers)
        submission_id = submit_response.json()["data"]["id"]
        
        # Admin approves submission
        moderation_data = {
            "status": "approved",
            "feedback": "Great work! Task completed successfully."
        }
        response = client.post(f"/api/admin/submissions/{submission_id}/review", json=moderation_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_admin_reject_submission(self, client: TestClient, admin_headers, setup_test_db):
        """Test admin rejecting a submission"""
        # Setup task and submission (similar to above)
        task_data = {"title": "Rejectable Task", "description": "Task to reject", "xp_reward": 25}
        create_response = client.post("/api/tasks", json=task_data, headers=admin_headers)
        task_id = create_response.json()["data"]["id"]
        
        user_data = {"email": "submitter@example.com", "password": "Password123!", "display_name": "Submitter"}
        client.post("/api/auth/register", json=user_data)
        login = client.post("/api/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
        token = login.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post(f"/api/tasks/{task_id}/claim", headers=headers)
        submit_response = client.post(f"/api/tasks/{task_id}/submit", json={"proof": "Incomplete task"}, headers=headers)
        submission_id = submit_response.json()["data"]["id"]
        
        # Admin rejects submission
        moderation_data = {
            "status": "rejected",
            "feedback": "Task incomplete. Please provide more detailed proof."
        }
        response = client.post(f"/api/admin/submissions/{submission_id}/review", json=moderation_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

class TestTaskValidation:
    """Test input validation for tasks"""
    
    def test_create_task_missing_title(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating task without title"""
        invalid_task = {
            "description": "Task description",
            "xp_reward": 25
            # Missing title
        }
        
        response = client.post("/api/tasks", json=invalid_task, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_create_task_negative_xp(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating task with negative XP"""
        invalid_task = {
            "title": "Invalid Task",
            "description": "Task description",
            "xp_reward": -50  # Negative XP
        }
        
        response = client.post("/api/tasks", json=invalid_task, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_create_task_invalid_proof_type(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating task with invalid proof type"""
        invalid_task = {
            "title": "Invalid Task",
            "description": "Task description",
            "xp_reward": 25,
            "proof_type": "invalid_type"  # Invalid proof type
        }
        
        response = client.post("/api/tasks", json=invalid_task, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False

if __name__ == "__main__":
    pytest.main([__file__])
