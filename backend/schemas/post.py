from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Post content")
    media_url: Optional[str] = Field(None, description="Media URL (image/video)")
    post_type: str = Field(default="text", description="Post type (text, image, video)")
    language: str = Field(default="en", description="Post language (rw, en, fr, sw)")
    
    @validator('post_type')
    def validate_post_type(cls, v):
        if v not in ['text', 'image', 'video']:
            raise ValueError('Post type must be one of: text, image, video')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ['rw', 'en', 'fr', 'sw']:
            raise ValueError('Language must be one of: rw, en, fr, sw')
        return v

class PostUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000, description="Post content")
    media_url: Optional[str] = Field(None, description="Media URL")
    post_type: Optional[str] = Field(None, description="Post type")
    language: Optional[str] = Field(None, description="Post language")

class PostResponse(BaseModel):
    id: int = Field(..., description="Post ID")
    user_id: int = Field(..., description="User ID")
    content: str = Field(..., description="Post content")
    media_url: Optional[str] = Field(None, description="Media URL")
    post_type: str = Field(..., description="Post type")
    likes_count: int = Field(default=0, description="Number of likes")
    status: str = Field(..., description="Post status")
    language: str = Field(..., description="Post language")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user: Optional['UserResponse'] = Field(None, description="Post author")

class PostList(BaseModel):
    posts: List[PostResponse] = Field(default=[], description="List of posts")
    total: int = Field(..., description="Total number of posts")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Posts per page")

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Comment content")

class CommentResponse(BaseModel):
    id: int = Field(..., description="Comment ID")
    post_id: int = Field(..., description="Post ID")
    user_id: int = Field(..., description="User ID")
    content: str = Field(..., description="Comment content")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user: Optional['UserResponse'] = Field(None, description="Comment author")

class LikeResponse(BaseModel):
    id: int = Field(..., description="Like ID")
    post_id: int = Field(..., description="Post ID")
    user_id: int = Field(..., description="User ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")

class PostModeration(BaseModel):
    status: str = Field(..., description="Moderation status (approved, rejected)")
    reason: Optional[str] = Field(None, description="Moderation reason")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError('Status must be approved or rejected')
        return v

class PostStats(BaseModel):
    total_posts: int = Field(default=0, description="Total posts")
    approved_posts: int = Field(default=0, description="Approved posts")
    pending_posts: int = Field(default=0, description="Pending posts")
    rejected_posts: int = Field(default=0, description="Rejected posts")
    posts_today: int = Field(default=0, description="Posts created today")
    top_languages: List[dict] = Field(default=[], description="Most used languages")

class FeedFilter(BaseModel):
    language: Optional[str] = Field(None, description="Filter by language")
    status: Optional[str] = Field(None, description="Filter by status")
    user_id: Optional[int] = Field(None, description="Filter by user")
    date_from: Optional[datetime] = Field(None, description="Filter posts from date")
    date_to: Optional[datetime] = Field(None, description="Filter posts to date")
