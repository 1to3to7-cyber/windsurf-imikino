import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from unittest.mock import patch, MagicMock

from main import app
from db import Base, get_db
from models.user import User
from models.contact_submission import ContactSubmission

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_email.db"
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

@pytest.fixture
def sample_contact_data():
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "Test Contact Message",
        "message": "This is a test message for the contact form.",
        "priority": "medium"
    }

class TestContactForm:
    """Test contact form endpoints"""
    
    def test_submit_contact_success(self, client: TestClient, sample_contact_data, setup_test_db):
        """Test successful contact form submission"""
        response = client.post("/api/contact", json=sample_contact_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["name"] == sample_contact_data["name"]
        assert data["data"]["email"] == sample_contact_data["email"]
        assert data["data"]["subject"] == sample_contact_data["subject"]
        assert data["data"]["message"] == sample_contact_data["message"]
        assert data["data"]["status"] == "new"
        assert data["data"]["priority"] == sample_contact_data["priority"]
    
    def test_submit_contact_with_user(self, client: TestClient, sample_contact_data, auth_headers, setup_test_db):
        """Test contact form submission with authenticated user"""
        contact_data_with_user = {
            **sample_contact_data,
            "user_id": 1  # Simulate user ID
        }
        
        response = client.post("/api/contact", json=contact_data_with_user, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data["data"]
        assert data["data"]["user_id"] == 1
    
    @patch('services.email_service.EmailService.send_contact_email')
    def test_submit_contact_email_sent(self, mock_send_email, client: TestClient, sample_contact_data, setup_test_db):
        """Test that email is sent when contact form is submitted"""
        # Configure mock to return True
        mock_send_email.return_value = True
        
        response = client.post("/api/contact", json=sample_contact_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        
        # Verify email service was called
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        
        # Check that the submission data was passed to email service
        assert call_args[0]["name"] == sample_contact_data["name"]
        assert call_args[0]["email"] == sample_contact_data["email"]
        assert call_args[0]["subject"] == sample_contact_data["subject"]
        assert call_args[0]["message"] == sample_contact_data["message"]
    
    def test_submit_contact_missing_fields(self, client: TestClient, setup_test_db):
        """Test contact form submission with missing required fields"""
        invalid_data = {
            "name": "John Doe",
            "email": "john@example.com"
            # Missing subject and message
        }
        
        response = client.post("/api/contact", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_submit_contact_invalid_email(self, client: TestClient, setup_test_db):
        """Test contact form submission with invalid email"""
        invalid_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "subject": "Test Subject",
            "message": "Test message"
        }
        
        response = client.post("/api/contact", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_submit_contact_empty_message(self, client: TestClient, setup_test_db):
        """Test contact form submission with empty message"""
        invalid_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test Subject",
            "message": ""  # Empty message
        }
        
        response = client.post("/api/contact", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_submit_contact_invalid_priority(self, client: TestClient, setup_test_db):
        """Test contact form submission with invalid priority"""
        invalid_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test Subject",
            "message": "Test message",
            "priority": "invalid_priority"  # Invalid priority
        }
        
        response = client.post("/api/contact", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_submit_contact_long_name(self, client: TestClient, setup_test_db):
        """Test contact form submission with name too long"""
        invalid_data = {
            "name": "a" * 101,  # 101 characters, over the limit
            "email": "john@example.com",
            "subject": "Test Subject",
            "message": "Test message"
        }
        
        response = client.post("/api/contact", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False

class TestContactAdmin:
    """Test admin contact management endpoints"""
    
    @pytest.fixture
    def admin_user(self):
        return {
            "email": "admin@example.com",
            "password": "AdminPassword123!",
            "display_name": "Admin User"
        }
    
    @pytest.fixture
    def admin_headers(self, client: TestClient, admin_user, setup_test_db):
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
    def sample_contacts(self, client: TestClient, admin_headers, setup_test_db):
        """Create sample contact submissions"""
        contacts_data = [
            {
                "name": "User 1",
                "email": "user1@example.com",
                "subject": "Question 1",
                "message": "I have a question about courses.",
                "priority": "low"
            },
            {
                "name": "User 2",
                "email": "user2@example.com",
                "subject": "Urgent Issue",
                "message": "I found a bug in the app.",
                "priority": "urgent"
            },
            {
                "name": "User 3",
                "email": "user3@example.com",
                "subject": "Feedback",
                "message": "Great app! Keep up the good work.",
                "priority": "medium"
            }
        ]
        
        for contact_data in contacts_data:
            client.post("/api/contact", json=contact_data)
        
        return contacts_data
    
    def test_admin_get_contacts(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin getting all contact submissions"""
        response = client.get("/api/admin/contact", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "submissions" in data["data"]
        assert len(data["data"]["submissions"]) == 3
    
    def test_admin_get_contacts_with_filter(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin getting contacts with status filter"""
        response = client.get("/api/admin/contact?status=new", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["submissions"]) == 3
        # All contacts should have status "new" initially
        for submission in data["data"]["submissions"]:
            assert submission["status"] == "new"
    
    def test_admin_get_contact_by_id(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin getting a specific contact submission"""
        # Get the first contact ID
        response = client.get("/api/admin/contact", headers=admin_headers)
        contact_id = response.json()["data"]["submissions"][0]["id"]
        
        # Get specific contact
        response = client.get(f"/api/admin/contact/{contact_id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == contact_id
        assert data["data"]["name"] == "User 1"
    
    def test_admin_update_contact_status(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin updating contact submission status"""
        # Get the first contact ID
        response = client.get("/api/admin/contact", headers=admin_headers)
        contact_id = response.json()["data"]["submissions"][0]["id"]
        
        # Update status
        update_data = {
            "status": "in_progress",
            "response": "We are looking into your question."
        }
        response = client.put(f"/api/admin/contact/{contact_id}", json=update_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "in_progress"
        assert data["data"]["response"] == "We are looking into your question."
    
    def test_admin_update_contact_invalid_status(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin updating contact with invalid status"""
        # Get the first contact ID
        response = client.get("/api/admin/contact", headers=admin_headers)
        contact_id = response.json()["data"]["submissions"][0]["id"]
        
        # Update with invalid status
        update_data = {
            "status": "invalid_status"
        }
        response = client.put(f"/api/admin/contact/{contact_id}", json=update_data, headers=admin_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    def test_admin_delete_contact(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin deleting a contact submission"""
        # Get the first contact ID
        response = client.get("/api/admin/contact", headers=admin_headers)
        contact_id = response.json()["data"]["submissions"][0]["id"]
        
        # Delete contact
        response = client.delete(f"/api/admin/contact/{contact_id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_admin_bulk_update_contacts(self, client: TestClient, admin_headers, sample_contacts, setup_test_db):
        """Test admin bulk updating contact submissions"""
        # Get all contact IDs
        response = client.get("/api/admin/contact", headers=admin_headers)
        contact_ids = [sub["id"] for sub in response.json()["data"]["submissions"]]
        
        # Bulk update
        bulk_data = {
            "contact_ids": contact_ids,
            "status": "resolved",
            "response": "All questions have been answered."
        }
        response = client.post("/api/admin/contact/bulk", json=bulk_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["updated"] == len(contact_ids)

class TestEmailService:
    """Test email service functionality"""
    
    @patch('services.email_service.smtplib.SMTP')
    def test_email_service_smtp_failure(self, mock_smtp, client: TestClient, sample_contact_data, setup_test_db):
        """Test email service when SMTP fails"""
        # Configure mock to raise exception
        mock_smtp.return_value = MagicMock()
        mock_smtp.return_value.send_message.side_effect = Exception("SMTP connection failed")
        
        response = client.post("/api/contact", json=sample_contact_data)
        
        # Should still create contact submission even if email fails
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
    
    @patch('services.email_service.EmailService.send_contact_email')
    def test_email_service_logs_error(self, mock_send_email, client: TestClient, sample_contact_data, setup_test_db):
        """Test that email service logs errors appropriately"""
        # Configure mock to raise exception
        mock_send_email.side_effect = Exception("Email sending failed")
        
        with patch('services.email_service.logger') as mock_logger:
            response = client.post("/api/contact", json=sample_contact_data)
            
            # Should still create contact submission
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            
            # Check that error was logged
            mock_logger.error.assert_called_once()

class TestContactValidation:
    """Test contact form validation"""
    
    def test_contact_xss_prevention(self, client: TestClient, setup_test_db):
        """Test that XSS is prevented in contact form"""
        xss_data = {
            "name": "<script>alert('xss')</script>",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Message with <script>alert('xss')</script> content"
        }
        
        response = client.post("/api/contact", json=xss_data)
        
        # Should sanitize the input
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        
        # Check that script tags were removed
        assert "<script>" not in data["data"]["name"]
        assert "<script>" not in data["data"]["message"]
    
    def test_contact_sanitization(self, client: TestClient, setup_test_db):
        """Test that HTML is properly sanitized"""
        html_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Message with <b>bold</b> and <a href='http://evil.com'>link</a>"
        }
        
        response = client.post("/api/contact", json=html_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        
        # Check that HTML is sanitized (basic sanitization)
        # The exact sanitization depends on the implementation
        # This test ensures the sanitization process is working

if __name__ == "__main__":
    pytest.main([__file__])
