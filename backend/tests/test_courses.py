import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from main import app
from db import Base, get_db
from models.user import User
from models.course import Course, Module, Quiz
from models.progress import Progress

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_courses.db"
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
def sample_course():
    return {
        "title": "Test Course",
        "description": "This is a test course for learning",
        "xp_reward": 100,
        "thumbnail": "https://example.com/course-thumb.jpg"
    }

@pytest.fixture
def sample_module():
    return {
        "title": "Test Module",
        "content": "This is test module content",
        "type": "text",
        "order_index": 1
    }

@pytest.fixture
def sample_quiz():
    return {
        "questions": [
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct": 1
            },
            {
                "question": "What is the capital of Rwanda?",
                "options": ["Kigali", "Nairobi", "Kampala", "Dar es Salaam"],
                "correct": 0
            }
        ],
        "answers": [0, 1],
        "xp_reward": 25,
        "passing_score": 70,
        "time_limit": 30
    }

class TestCourses:
    """Test courses endpoints"""
    
    def test_get_courses_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting courses list"""
        response = client.get("/api/courses", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "courses" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "limit" in data["data"]
    
    def test_get_courses_with_pagination(self, client: TestClient, auth_headers, setup_test_db):
        """Test courses pagination"""
        response = client.get("/api/courses?page=1&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 5
    
    def test_get_course_by_id_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting a specific course"""
        # Create a course first
        course_data = {
            "title": "Test Course",
            "description": "Test description",
            "xp_reward": 50
        }
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        # Get the course
        response = client.get(f"/api/courses/{course_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == course_id
        assert data["data"]["title"] == course_data["title"]
    
    def test_get_course_not_found(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting a non-existent course"""
        response = client.get("/api/courses/99999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_create_course_success(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating a course"""
        course_data = {
            "title": "New Course",
            "description": "Course description",
            "xp_reward": 75,
            "thumbnail": "https://example.com/thumb.jpg"
        }
        
        response = client.post("/api/courses", json=course_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["title"] == course_data["title"]
        assert data["data"]["xp_reward"] == course_data["xp_reward"]
    
    def test_create_course_unauthorized(self, client: TestClient, auth_headers, setup_test_db):
        """Test creating a course without admin rights"""
        course_data = {
            "title": "New Course",
            "description": "Course description",
            "xp_reward": 75
        }
        
        response = client.post("/api/courses", json=course_data, headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
    
    def test_create_course_invalid_data(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating a course with invalid data"""
        invalid_course = {
            "title": "",  # Empty title
            "description": "Course description",
            "xp_reward": -50  # Negative XP
        }
        
        response = client.post("/api/courses", json=invalid_course, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False

class TestModules:
    """Test modules endpoints"""
    
    def test_get_course_modules_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting modules for a course"""
        # Create a course first
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        # Get modules
        response = client.get(f"/api/courses/{course_id}/modules", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modules" in data["data"]
    
    def test_create_module_success(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating a module"""
        # Create a course first
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=admin_headers)
        course_id = create_response.json()["data"]["id"]
        
        # Create module
        module_data = {
            "title": "Test Module",
            "content": "Module content",
            "type": "text",
            "order_index": 1
        }
        
        response = client.post(f"/api/courses/{course_id}/modules", json=module_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == module_data["title"]
        assert data["data"]["course_id"] == course_id

class TestQuizzes:
    """Test quiz endpoints"""
    
    def test_get_module_quiz_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting quiz for a module"""
        # Create course and module with quiz
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        module_data = {"title": "Test Module", "content": "Module content", "type": "quiz", "order_index": 1}
        module_response = client.post(f"/api/courses/{course_id}/modules", json=module_data, headers=auth_headers)
        module_id = module_response.json()["data"]["id"]
        
        # Create quiz
        quiz_data = {
            "questions": [
                {"question": "Test question", "options": ["A", "B", "C", "D"], "correct": 0}
            ],
            "answers": [0],
            "xp_reward": 25,
            "passing_score": 70
        }
        quiz_response = client.post(f"/api/courses/{course_id}/modules/{module_id}/quiz", json=quiz_data, headers=auth_headers)
        
        # Get quiz
        response = client.get(f"/api/courses/{course_id}/modules/{module_id}/quiz", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "questions" in data["data"]
    
    def test_submit_quiz_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test submitting quiz answers"""
        # Setup course, module, and quiz
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        module_data = {"title": "Test Module", "content": "Module content", "type": "quiz", "order_index": 1}
        module_response = client.post(f"/api/courses/{course_id}/modules", json=module_data, headers=auth_headers)
        module_id = module_response.json()["data"]["id"]
        
        quiz_data = {
            "questions": [
                {"question": "What is 2+2?", "options": ["3", "4", "5"], "correct": 0}
            ],
            "answers": [0],
            "xp_reward": 25,
            "passing_score": 70
        }
        quiz_response = client.post(f"/api/courses/{course_id}/modules/{module_id}/quiz", json=quiz_data, headers=auth_headers)
        
        # Submit quiz answers
        submission_data = {"answers": [0]}
        response = client.post(f"/api/courses/{course_id}/modules/{module_id}/quiz/submit", json=submission_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "score" in data["data"]
        assert "passed" in data["data"]
        assert "xp_awarded" in data["data"]
    
    def test_submit_quiz_wrong_answers(self, client: TestClient, auth_headers, setup_test_db):
        """Test submitting quiz with wrong answers"""
        # Setup course, module, and quiz
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        module_data = {"title": "Test Module", "content": "Module content", "type": "quiz", "order_index": 1}
        module_response = client.post(f"/api/courses/{course_id}/modules", json=module_data, headers=auth_headers)
        module_id = module_response.json()["data"]["id"]
        
        quiz_data = {
            "questions": [
                {"question": "What is 2+2?", "options": ["3", "4", "5"], "correct": 0}
            ],
            "answers": [0],
            "xp_reward": 25,
            "passing_score": 70
        }
        quiz_response = client.post(f"/api/courses/{course_id}/modules/{module_id}/quiz", json=quiz_data, headers=auth_headers)
        
        # Submit wrong answers
        submission_data = {"answers": [1]}  # Wrong answer
        response = client.post(f"/api/courses/{course_id}/modules/{module_id}/quiz/submit", json=submission_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["passed"] is False
        assert data["data"]["score"] < 70

class TestProgress:
    """Test progress tracking"""
    
    def test_mark_module_complete_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test marking a module as complete"""
        # Setup course and module
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        module_data = {"title": "Test Module", "content": "Module content", "type": "text", "order_index": 1}
        module_response = client.post(f"/api/courses/{course_id}/modules", json=module_data, headers=auth_headers)
        module_id = module_response.json()["data"]["id"]
        
        # Mark module complete
        response = client.post(f"/api/courses/{course_id}/modules/{module_id}/complete", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["completed"] is True
    
    def test_get_user_progress(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting user progress"""
        response = client.get("/api/courses/progress", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "completed_courses" in data["data"]
        assert "completed_modules" in data["data"]
        assert "total_xp" in data["data"]
    
    def test_get_course_progress(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting progress for a specific course"""
        # Create a course first
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=auth_headers)
        course_id = create_response.json()["data"]["id"]
        
        # Get course progress
        response = client.get(f"/api/courses/{course_id}/progress", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "progress" in data["data"]
        assert "completion_percentage" in data["data"]

class TestCourseValidation:
    """Test input validation for courses"""
    
    def test_create_course_missing_title(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating course without title"""
        invalid_course = {
            "description": "Course description",
            "xp_reward": 50
            # Missing title
        }
        
        response = client.post("/api/courses", json=invalid_course, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_create_course_negative_xp(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating course with negative XP"""
        invalid_course = {
            "title": "Test Course",
            "description": "Course description",
            "xp_reward": -50  # Negative XP
        }
        
        response = client.post("/api/courses", json=invalid_course, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_create_module_invalid_type(self, client: TestClient, admin_headers, setup_test_db):
        """Test creating module with invalid type"""
        # Create a course first
        course_data = {"title": "Test Course", "description": "Test", "xp_reward": 50}
        create_response = client.post("/api/courses", json=course_data, headers=admin_headers)
        course_id = create_response.json()["data"]["id"]
        
        invalid_module = {
            "title": "Test Module",
            "content": "Module content",
            "type": "invalid_type",  # Invalid type
            "order_index": 1
        }
        
        response = client.post(f"/api/courses/{course_id}/modules", json=invalid_module, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False

if __name__ == "__main__":
    pytest.main([__file__])
