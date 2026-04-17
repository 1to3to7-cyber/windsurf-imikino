from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class AdminStats(BaseModel):
    total_users: int = Field(default=0, description="Total registered users")
    active_users: int = Field(default=0, description="Active users (last 30 days)")
    new_users_today: int = Field(default=0, description="New users registered today")
    total_posts: int = Field(default=0, description="Total posts created")
    pending_posts: int = Field(default=0, description="Posts pending moderation")
    total_tasks: int = Field(default=0, description="Total tasks created")
    open_tasks: int = Field(default=0, description="Open tasks")
    completed_tasks: int = Field(default=0, description="Completed tasks")
    pending_submissions: int = Field(default=0, description="Task submissions pending review")
    total_courses: int = Field(default=0, description="Total courses")
    completed_courses: int = Field(default=0, description="Completed courses")
    total_xp_awarded: int = Field(default=0, description="Total XP points awarded")
    contact_submissions: int = Field(default=0, description="Contact submissions")
    pending_contact: int = Field(default=0, description="Pending contact submissions")

class UserManagement(BaseModel):
    user_id: int = Field(..., description="User ID to manage")
    role: Optional[str] = Field(None, description="New role (user, moderator, admin)")
    is_active: Optional[bool] = Field(None, description="Account active status")
    xp_adjustment: Optional[int] = Field(None, description="XP adjustment (positive or negative)")
    
    @validator('role')
    def validate_role(cls, v):
        if v and v not in ['user', 'moderator', 'admin']:
            raise ValueError('Role must be one of: user, moderator, admin')
        return v

class PostModeration(BaseModel):
    post_id: int = Field(..., description="Post ID to moderate")
    status: str = Field(..., description="Moderation status (approved, rejected)")
    reason: Optional[str] = Field(None, max_length=500, description="Moderation reason")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError('Status must be approved or rejected')
        return v

class SubmissionReview(BaseModel):
    submission_id: int = Field(..., description="Submission ID to review")
    status: str = Field(..., description="Review status (approved, rejected)")
    feedback: Optional[str] = Field(None, max_length=1000, description="Feedback for user")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError('Status must be approved or rejected')
        return v

class BulkUserAction(BaseModel):
    user_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of user IDs")
    action: str = Field(..., description="Action to perform")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for action")
    
    @validator('action')
    def validate_action(cls, v):
        if v not in ['activate', 'deactivate', 'delete', 'promote', 'demote']:
            raise ValueError('Action must be one of: activate, deactivate, delete, promote, demote')
        return v

class SystemConfig(BaseModel):
    site_name: Optional[str] = Field(None, max_length=100, description="Site name")
    site_description: Optional[str] = Field(None, max_length=500, description="Site description")
    maintenance_mode: Optional[bool] = Field(None, description="Maintenance mode status")
    registration_enabled: Optional[bool] = Field(None, description="Allow new user registration")
    post_moderation: Optional[bool] = Field(None, description="Require post moderation")
    xp_multiplier: Optional[float] = Field(None, ge=0.1, le=10.0, description="XP multiplier for rewards")
    
    @validator('xp_multiplier')
    def validate_xp_multiplier(cls, v):
        if v is not None and (v < 0.1 or v > 10.0):
            raise ValueError('XP multiplier must be between 0.1 and 10.0')
        return v

class AuditLogFilter(BaseModel):
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    action: Optional[str] = Field(None, description="Filter by action")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    success: Optional[str] = Field(None, description="Filter by success status")
    date_from: Optional[datetime] = Field(None, description="Filter logs from date")
    date_to: Optional[datetime] = Field(None, description="Filter logs to date")
    ip_address: Optional[str] = Field(None, description="Filter by IP address")

class Analytics(BaseModel):
    period: str = Field(default="7d", description="Time period (1d, 7d, 30d)")
    total_users: int = Field(default=0, description="Total users in period")
    new_users: int = Field(default=0, description="New users in period")
    active_users: int = Field(default=0, description="Active users in period")
    total_sessions: int = Field(default=0, description="Total sessions in period")
    total_posts: int = Field(default=0, description="Total posts in period")
    total_tasks_completed: int = Field(default=0, description="Total tasks completed in period")
    total_xp_awarded: int = Field(default=0, description="Total XP awarded in period")
    average_session_duration: Optional[float] = Field(None, description="Average session duration in minutes")
    top_countries: List[dict] = Field(default=[], description="Top countries by users")
    top_languages: List[dict] = Field(default=[], description="Most used languages")
    
    @validator('period')
    def validate_period(cls, v):
        if v not in ['1d', '7d', '30d']:
            raise ValueError('Period must be one of: 1d, 7d, 30d')
        return v
