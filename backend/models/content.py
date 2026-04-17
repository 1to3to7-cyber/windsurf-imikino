from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Content(Base):
    __tablename__ = "user_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Foreign key to users
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # post, article, video, image, document
    file_url = Column(String(500), nullable=True)  # For media files
    thumbnail_url = Column(String(500), nullable=True)
    tags = Column(JSON, default=list)  # List of tags
    category = Column(String(100), nullable=True)
    visibility = Column(String(20), default="public", nullable=False)  # public, private, unlisted
    social_sharing = Column(JSON, default=dict)  # Social media sharing settings
    likes_count = Column(Integer, default=0, nullable=False)
    shares_count = Column(Integer, default=0, nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    comments_count = Column(Integer, default=0, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="draft", nullable=False)  # draft, published, archived
    moderation_status = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Social media integration fields
    social_platforms = Column(JSON, default=dict)  # Where content is shared
    engagement_score = Column(Float, default=0.0, nullable=False)  # AI-calculated engagement score
    trending_score = Column(Float, default=0.0, nullable=False)  # AI-calculated trending score
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "content_type": self.content_type,
            "file_url": self.file_url,
            "thumbnail_url": self.thumbnail_url,
            "tags": self.tags or [],
            "category": self.category,
            "visibility": self.visibility,
            "social_sharing": self.social_sharing or {},
            "likes_count": self.likes_count,
            "shares_count": self.shares_count,
            "views_count": self.views_count,
            "comments_count": self.comments_count,
            "featured": self.featured,
            "status": self.status,
            "moderation_status": self.moderation_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "social_platforms": self.social_platforms or {},
            "engagement_score": self.engagement_score,
            "trending_score": self.trending_score
        }
    
    def __repr__(self):
        return f"<Content(id={self.id}, title={self.title[:50]}..., type={self.content_type})>"
