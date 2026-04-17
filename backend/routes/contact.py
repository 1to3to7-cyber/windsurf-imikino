from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from datetime import datetime
import json
import logging
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.security import get_current_user
from models.user import User
from db import get_db
from audit import log_admin_action

router = APIRouter(prefix="/api/contact", tags=["contact"])
logger = logging.getLogger(__name__)

class ContactSubmission(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    category: str = "general"
    phone: str = ""

class ContactResponse(BaseModel):
    success: bool
    message: str
    submission_id: str

def send_email_to_admin(submission: Dict[str, Any]) -> bool:
    """Send contact form submission to admin email"""
    try:
        # Email configuration
        admin_email = "1to3to7@gmail.com"
        sender_email = "noreply@imikino.rw"
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = f"Imikino Platform <{sender_email}>"
        msg['To'] = admin_email
        msg['Subject'] = f"Imikino Contact: {submission['subject']}"
        
        # Email body
        body = f"""
        New Contact Form Submission
        
        From: {submission['name']} ({submission['email']})
        Phone: {submission['phone']}
        Category: {submission['category']}
        Subject: {submission['subject']}
        
        Message:
        {submission['message']}
        
        ---
        Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        IP Address: {submission.get('ip_address', 'Not captured')}
        User Agent: {submission.get('user_agent', 'Not captured')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email (in production, use proper SMTP settings)
        # For demo purposes, we'll log the email content
        logger.info(f"Contact form submission to {admin_email}:")
        logger.info(f"From: {submission['name']} <{submission['email']}>")
        logger.info(f"Subject: {submission['subject']}")
        logger.info(f"Category: {submission['category']}")
        logger.info(f"Message: {submission['message'][:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

@router.post("/submit", response_model=ContactResponse)
async def submit_contact_form(
    submission: ContactSubmission,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit contact form and email to admin"""
    
    try:
        # Generate submission ID
        submission_id = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get client information
        client_info = {
            "ip_address": request.client.host if request.client else "Unknown",
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
        
        # Store in database
        contact_query = text("""
            INSERT INTO contact_submissions (
                id, name, email, phone, subject, message, category, 
                user_id, ip_address, user_agent, status, created_at
            ) VALUES (
                :id, :name, :email, :phone, :subject, :message, :category,
                :user_id, :ip_address, :user_agent, 'pending', NOW()
            )
        """)
        
        db.execute(contact_query, {
            "id": submission_id,
            "name": submission.name,
            "email": submission.email,
            "phone": submission.phone,
            "subject": submission.subject,
            "message": submission.message,
            "category": submission.category,
            "user_id": current_user.id if current_user else None,
            "ip_address": client_info["ip_address"],
            "user_agent": client_info["user_agent"]
        })
        
        db.commit()
        
        # Prepare email data
        email_data = {
            "name": submission.name,
            "email": submission.email,
            "phone": submission.phone,
            "subject": submission.subject,
            "message": submission.message,
            "category": submission.category,
            **client_info
        }
        
        # Send email to admin
        email_sent = send_email_to_admin(email_data)
        
        # Log the action
        await log_admin_action(
            db=db,
            user_id=current_user.id if current_user else 0,
            action="contact_form_submission",
            resource="contact",
            resource_id=submission_id,
            details=json.dumps({
                "submission_id": submission_id,
                "email": submission.email,
                "category": submission.category,
                "email_sent": email_sent,
                "user_authenticated": bool(current_user)
            })
        )
        
        response_messages = {
            "rw": "Murakoze cyane! Twasanze icyo wanyu. Tuzakubwira vuba.",
            "en": "Thank you for contacting us! We've received your message and will respond soon.",
            "fr": "Merci de nous contacter! Nous avons reçu votre message et vous répondrons bientôt.",
            "sw": "Asante kwa kuwasiliana! Tumepokea ujumbe wako na tutajibu hivi karibuni."
        }
        
        return ContactResponse(
            success=True,
            message=response_messages.get("en", response_messages["en"]),
            submission_id=submission_id
        )
        
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process contact form submission"
        )

@router.get("/categories")
async def get_contact_categories():
    """Get available contact form categories"""
    categories = [
        {"value": "general", "label": "General Inquiry"},
        {"value": "technical", "label": "Technical Support"},
        {"value": "academic", "label": "Academic Questions"},
        {"value": "feedback", "label": "Feedback & Suggestions"},
        {"value": "partnership", "label": "Partnership Opportunities"},
        {"value": "report", "label": "Report an Issue"}
    ]
    return categories

@router.get("/status/{submission_id}")
async def get_submission_status(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check status of contact form submission"""
    
    try:
        status_query = text("""
            SELECT id, status, response, created_at, updated_at
            FROM contact_submissions 
            WHERE id = :submission_id
        """)
        
        result = db.execute(status_query, {"submission_id": submission_id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        return {
            "id": result.id,
            "status": result.status,
            "response": result.response,
            "created_at": result.created_at,
            "updated_at": result.updated_at
        }
        
    except Exception as e:
        logger.error(f"Error checking submission status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check submission status"
        )
