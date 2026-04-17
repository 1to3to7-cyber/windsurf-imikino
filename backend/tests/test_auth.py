import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt

from main import app
from db import Base, get_db
from models.user import User
from core.security import get_password_hash, verify_password, create_access_token, verify_token

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, client: TestClient, test_user, setup_test_db):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["email"] == test_user["email"]
        assert data["data"]["display_name"] == test_user["display_name"]
        assert data["data"]["role"] == "user"
        assert data["data"]["xp"] == 0
        assert data["data"]["level"] == 1
    
    def test_register_user_duplicate_email(self, client: TestClient, test_user, setup_test_db):
        """Test registration with duplicate email"""
        # First registration
        client.post("/api/auth/register", json=test_user)
        
        # Second registration with same email
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Email already registered" in data["error"]["message"]
    
    def test_register_user_invalid_email(self, client: TestClient, setup_test_db):
        """Test registration with invalid email"""
        invalid_user = {
            "email": "invalid-email",
            "password": "TestPassword123!",
            "display_name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=invalid_user)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_register_user_weak_password(self, client: TestClient, setup_test_db):
        """Test registration with weak password"""
        weak_user = {
            "email": "test@example.com",
            "password": "123",
            "display_name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=weak_user)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_login_success(self, client: TestClient, test_user, setup_test_db):
        """Test successful login"""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]
    
    def test_login_invalid_credentials(self, client: TestClient, test_user, setup_test_db):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/auth/register", json=test_user)
        
        # Login with wrong password
        login_data = {
            "email": test_user["email"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Invalid credentials" in data["error"]["message"]
    
    def test_login_nonexistent_user(self, client: TestClient, setup_test_db):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Invalid credentials" in data["error"]["message"]
    
    def test_refresh_token_success(self, client: TestClient, test_user, setup_test_db):
        """Test successful token refresh"""
        # Register and login user
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Refresh token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client: TestClient, setup_test_db):
        """Test refresh with invalid token"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    def test_protected_endpoint_without_token(self, client: TestClient, setup_test_db):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/users/me")
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    def test_protected_endpoint_with_valid_token(self, client: TestClient, test_user, setup_test_db):
        """Test accessing protected endpoint with valid token"""
        # Register and login user
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user["email"]
    
    def test_protected_endpoint_with_invalid_token(self, client: TestClient, setup_test_db):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

class TestSecurity:
    """Test security features"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hash length
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_jwt_token_creation(self):
        """Test JWT token creation and verification"""
        user_data = {"sub": "test@example.com", "role": "user", "user_id": 1}
        token = create_access_token(data=user_data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT token length
        
        # Verify token
        payload = verify_token(token)
        assert payload["sub"] == user_data["sub"]
        assert payload["role"] == user_data["role"]
        assert payload["user_id"] == user_data["user_id"]
    
    def test_jwt_token_expiration(self):
        """Test JWT token expiration"""
        user_data = {"sub": "test@example.com", "role": "user", "user_id": 1}
        token = create_access_token(data=user_data, expires_delta=timedelta(seconds=1))
        
        # Token should be valid immediately
        payload = verify_token(token)
        assert payload is not None
        
        # Wait for token to expire
        import time
        time.sleep(2)
        
        # Token should be expired
        with pytest.raises(Exception):
            verify_token(token)

class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limiting_login(self, client: TestClient, setup_test_db):
        """Test rate limiting on login endpoint"""
        # Make multiple rapid requests
        responses = []
        for _ in range(110):  # More than the rate limit
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            responses.append(response.status_code)
        
        # Should hit rate limit
        assert 429 in responses
        rate_limited_responses = [r for r in responses if r == 429]
        assert len(rate_limited_responses) > 0

class TestInputValidation:
    """Test input validation"""
    
    def test_register_missing_fields(self, client: TestClient, setup_test_db):
        """Test registration with missing required fields"""
        incomplete_user = {
            "email": "test@example.com"
            # Missing password and display_name
        }
        
        response = client.post("/api/auth/register", json=incomplete_user)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_register_long_display_name(self, client: TestClient, setup_test_db):
        """Test registration with display name too long"""
        invalid_user = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "a" * 51  # 51 characters, over the limit
        }
        
        response = client.post("/api/auth/register", json=invalid_user)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_register_invalid_characters_display_name(self, client: TestClient, setup_test_db):
        """Test registration with invalid characters in display name"""
        invalid_user = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test<script>alert('xss')</script>"
        }
        
        response = client.post("/api/auth/register", json=invalid_user)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False

if __name__ == "__main__":
    pytest.main([__file__])
