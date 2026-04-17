import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from main import app
from db import Base, get_db
from models.user import User
from models.post import Post, Comment, Like

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_posts.db"
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

class TestPosts:
    """Test posts endpoints"""
    
    def test_create_post_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test successful post creation"""
        post_data = {
            "content": "This is a test post",
            "post_type": "text",
            "language": "en"
        }
        
        response = client.post("/api/posts", json=post_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["content"] == post_data["content"]
        assert data["data"]["post_type"] == post_data["post_type"]
        assert data["data"]["language"] == post_data["language"]
        assert data["data"]["likes_count"] == 0
        assert data["data"]["status"] == "pending"
    
    def test_create_post_with_media(self, client: TestClient, auth_headers, setup_test_db):
        """Test post creation with media"""
        post_data = {
            "content": "Test post with image",
            "media_url": "https://example.com/image.jpg",
            "post_type": "image",
            "language": "rw"
        }
        
        response = client.post("/api/posts", json=post_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["media_url"] == post_data["media_url"]
        assert data["data"]["post_type"] == "image"
        assert data["data"]["language"] == "rw"
    
    def test_create_post_unauthorized(self, client: TestClient, setup_test_db):
        """Test post creation without authentication"""
        post_data = {
            "content": "This is a test post",
            "post_type": "text"
        }
        
        response = client.post("/api/posts", json=post_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    def test_create_post_empty_content(self, client: TestClient, auth_headers, setup_test_db):
        """Test post creation with empty content"""
        post_data = {
            "content": "",
            "post_type": "text"
        }
        
        response = client.post("/api/posts", json=post_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_get_posts_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting posts feed"""
        # Create some posts first
        posts_data = [
            {"content": "Post 1", "post_type": "text", "language": "en"},
            {"content": "Post 2", "post_type": "text", "language": "rw"},
            {"content": "Post 3", "post_type": "image", "language": "fr", "media_url": "https://example.com/image.jpg"}
        ]
        
        for post_data in posts_data:
            client.post("/api/posts", json=post_data, headers=auth_headers)
        
        # Get posts
        response = client.get("/api/posts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "posts" in data["data"]
        assert len(data["data"]["posts"]) == 3
        assert data["data"]["total"] == 3
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 20
    
    def test_get_posts_with_language_filter(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting posts with language filter"""
        # Create posts in different languages
        posts_data = [
            {"content": "English post", "post_type": "text", "language": "en"},
            {"content": "Kinyarwanda post", "post_type": "text", "language": "rw"},
            {"content": "French post", "post_type": "text", "language": "fr"}
        ]
        
        for post_data in posts_data:
            client.post("/api/posts", json=post_data, headers=auth_headers)
        
        # Get posts with language filter
        response = client.get("/api/posts?language=rw", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["posts"]) == 1
        assert data["data"]["posts"][0]["language"] == "rw"
    
    def test_get_post_by_id_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting a specific post"""
        # Create a post
        post_data = {"content": "Test post", "post_type": "text", "language": "en"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Get the post
        response = client.get(f"/api/posts/{post_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == post_id
        assert data["data"]["content"] == post_data["content"]
    
    def test_get_post_not_found(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting a non-existent post"""
        response = client.get("/api/posts/99999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_like_post_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test liking a post"""
        # Create a post
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Like the post
        response = client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["liked"] is True
    
    def test_like_post_twice(self, client: TestClient, auth_headers, setup_test_db):
        """Test liking the same post twice"""
        # Create a post
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Like the post first time
        client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        
        # Try to like again
        response = client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
    
    def test_unlike_post_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test unliking a post"""
        # Create a post and like it
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        client.post(f"/api/posts/{post_id}/like", headers=auth_headers)
        
        # Unlike the post
        response = client.delete(f"/api/posts/{post_id}/like", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["liked"] is False
    
    def test_comment_on_post_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test commenting on a post"""
        # Create a post
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Comment on the post
        comment_data = {"content": "This is a test comment"}
        response = client.post(f"/api/posts/{post_id}/comments", json=comment_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == comment_data["content"]
        assert data["data"]["post_id"] == post_id
    
    def test_get_post_comments(self, client: TestClient, auth_headers, setup_test_db):
        """Test getting comments for a post"""
        # Create a post with comments
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        comments_data = [
            {"content": "Comment 1"},
            {"content": "Comment 2"},
            {"content": "Comment 3"}
        ]
        
        for comment_data in comments_data:
            client.post(f"/api/posts/{post_id}/comments", json=comment_data, headers=auth_headers)
        
        # Get comments
        response = client.get(f"/api/posts/{post_id}/comments", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
    
    def test_update_post_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test updating a post"""
        # Create a post
        post_data = {"content": "Original content", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Update the post
        update_data = {"content": "Updated content"}
        response = client.put(f"/api/posts/{post_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == update_data["content"]
    
    def test_update_post_unauthorized(self, client: TestClient, setup_test_db):
        """Test updating a post without authentication"""
        post_id = 1
        update_data = {"content": "Updated content"}
        
        response = client.put(f"/api/posts/{post_id}", json=update_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    def test_delete_post_success(self, client: TestClient, auth_headers, setup_test_db):
        """Test deleting a post"""
        # Create a post
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=auth_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Delete the post
        response = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_post_unauthorized(self, client: TestClient, setup_test_db):
        """Test deleting a post without authentication"""
        post_id = 1
        
        response = client.delete(f"/api/posts/{post_id}")
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

class TestPostModeration:
    """Test post moderation"""
    
    def test_admin_moderate_post_approve(self, client: TestClient, setup_test_db):
        """Test admin approving a post"""
        # Create admin user
        admin_data = {
            "email": "admin@example.com",
            "password": "AdminPassword123!",
            "display_name": "Admin User"
        }
        client.post("/api/auth/register", json=admin_data)
        admin_login = client.post("/api/auth/login", json={
            "email": admin_data["email"],
            "password": admin_data["password"]
        })
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a regular user and post
        user_data = {
            "email": "user@example.com",
            "password": "UserPassword123!",
            "display_name": "Regular User"
        }
        client.post("/api/auth/register", json=user_data)
        user_login = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        user_token = user_login.json()["data"]["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Create a post
        post_data = {"content": "Test post", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=user_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Admin approves the post
        moderation_data = {
            "status": "approved",
            "reason": "Good content"
        }
        response = client.post(f"/api/admin/posts/{post_id}/moderate", json=moderation_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_admin_moderate_post_reject(self, client: TestClient, setup_test_db):
        """Test admin rejecting a post"""
        # Setup admin and user (same as above)
        admin_data = {"email": "admin@example.com", "password": "AdminPassword123!", "display_name": "Admin User"}
        client.post("/api/auth/register", json=admin_data)
        admin_login = client.post("/api/auth/login", json={"email": admin_data["email"], "password": admin_data["password"]})
        admin_token = admin_login.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        user_data = {"email": "user@example.com", "password": "UserPassword123!", "display_name": "Regular User"}
        client.post("/api/auth/register", json=user_data)
        user_login = client.post("/api/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
        user_token = user_login.json()["data"]["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Create a post
        post_data = {"content": "Inappropriate content", "post_type": "text"}
        create_response = client.post("/api/posts", json=post_data, headers=user_headers)
        post_id = create_response.json()["data"]["id"]
        
        # Admin rejects the post
        moderation_data = {
            "status": "rejected",
            "reason": "Violates community guidelines"
        }
        response = client.post(f"/api/admin/posts/{post_id}/moderate", json=moderation_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

if __name__ == "__main__":
    pytest.main([__file__])
