from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ContactSubmission(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Contact name")
    email: str = Field(..., min_length=5, max_length=255, description="Contact email")
    subject: str = Field(..., min_length=5, max_length=200, description="Contact subject")
    message: str = Field(..., min_length=10, max_length=2000, description="Contact message")
    priority: str = Field(default="medium", description="Priority level (low, medium, high, urgent)")
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be one of: low, medium, high, urgent')
        return v

class ContactResponse(BaseModel):
    id: int = Field(..., description="Contact submission ID")
    name: str = Field(..., description="Contact name")
    email: str = Field(..., description="Contact email")
    subject: str = Field(..., description="Contact subject")
    message: str = Field(..., description="Contact message")
    user_data_snapshot: Optional[dict] = Field(None, description="User data snapshot at submission time")
    status: str = Field(..., description="Submission status")
    priority: str = Field(..., description="Priority level")
    assigned_to: Optional[int] = Field(None, description="Admin assigned to handle")
    response: Optional[str] = Field(None, description="Admin response")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user: Optional['UserResponse']] = Field(None, description="User who submitted")

class ContactUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Submission status")
    priority: Optional[str] = Field(None, description="Priority level")
    assigned_to: Optional[int] = Field(None, description="Admin assigned to handle")
    response: Optional[str] = Field(None, max_length=1000, description="Admin response")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['new', 'in_progress', 'resolved', 'closed']:
            raise ValueError('Status must be one of: new, in_progress, resolved, closed')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be one of: low, medium, high, urgent')
        return v

class ContactStats(BaseModel):
    total_submissions: int = Field(default=0, description="Total contact submissions")
    new_submissions: int = Field(default=0, description="New submissions")
    in_progress_submissions: int = Field(default=0, description="Submissions in progress")
    resolved_submissions: int = Field(default=0, description="Resolved submissions")
    closed_submissions: int = Field(default=0, description="Closed submissions")
    average_response_time: Optional[float] = Field(None, description="Average response time in hours")
    submissions_today: int = Field(default=0, description="Submissions received today")
    top_priorities: List[dict] = Field(default=[], description="Submissions by priority")

class ContactFilter(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status")
    priority: Optional[str] = Field(None, description="Filter by priority")
    assigned_to: Optional[int] = Field(None, description="Filter by assigned admin")
    date_from: Optional[datetime] = Field(None, description="Filter submissions from date")
    date_to: Optional[datetime] = Field(None, description="Filter submissions to date")
    user_id: Optional[int] = Field(None, description="Filter by user")

class EmailTemplate(BaseModel):
    to_email: str = Field(..., description="Recipient email")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")
    html_body: Optional[str] = Field(None, description="HTML email body")
    attachments: Optional[List[str]] = Field(None, description="List of attachment file paths")

class EmailLog(BaseModel):
    id: int = Field(..., description="Email log ID")
    to_email: str = Field(..., description="Recipient email")
    subject: str = Field(..., description="Email subject")
    status: str = Field(..., description="Email status (sent, failed, bounced)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    sent_at: Optional[datetime] = Field(None, description="Email sent timestamp")
    created_at: Optional[datetime] = Field(None, description="Log creation timestamp")
