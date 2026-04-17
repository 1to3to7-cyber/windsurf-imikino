from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserResponse(BaseModel):
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    display_name: str = Field(..., description="Display name")
    role: str = Field(..., description="User role")
    xp: int = Field(default=0, description="User XP points")
    level: int = Field(default=1, description="User level")
    badges: List[dict] = Field(default=[], description="User badges")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=50, description="Display name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if v and not v.strip():
            return None
        return v.strip() if v else v

class UserProfile(BaseModel):
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    display_name: str = Field(..., description="Display name")
    role: str = Field(..., description="User role")
    xp: int = Field(default=0, description="User XP points")
    level: int = Field(default=1, description="User level")
    badges: List[dict] = Field(default=[], description="User badges")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    
    # Additional profile data
    completed_courses: int = Field(default=0, description="Number of completed courses")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    total_posts: int = Field(default=0, description="Total number of posts")
    total_likes: int = Field(default=0, description="Total likes received")

class UserStats(BaseModel):
    total_users: int = Field(default=0, description="Total registered users")
    active_users: int = Field(default=0, description="Active users (last 30 days)")
    new_users_today: int = Field(default=0, description="New users registered today")
    total_posts: int = Field(default=0, description="Total posts created")
    total_tasks_completed: int = Field(default=0, description="Total tasks completed")
    total_xp_awarded: int = Field(default=0, description="Total XP points awarded")

class UserAdminUpdate(BaseModel):
    role: Optional[str] = Field(None, description="User role (user, moderator, admin)")
    is_active: Optional[bool] = Field(None, description="Account active status")
    xp_adjustment: Optional[int] = Field(None, description="XP adjustment (positive or negative)")
    
    @validator('role')
    def validate_role(cls, v):
        if v and v not in ['user', 'moderator', 'admin']:
            raise ValueError('Role must be one of: user, moderator, admin')
        return v

class Badge(BaseModel):
    id: str = Field(..., description="Badge ID")
    name: str = Field(..., description="Badge name")
    description: str = Field(..., description="Badge description")
    icon: str = Field(..., description="Badge icon URL or emoji")
    earned_at: Optional[datetime] = Field(None, description="Badge earned timestamp")

class Level(BaseModel):
    level: int = Field(..., description="Level number")
    title: str = Field(..., description="Level title")
    min_xp: int = Field(..., description="Minimum XP required")
    max_xp: int = Field(..., description="Maximum XP for this level")
    benefits: List[str] = Field(default=[], description="Level benefits")
