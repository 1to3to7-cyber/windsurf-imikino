from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    post_type = Column(String, default="text", nullable=False)  # text, image, video
    likes_count = Column(Integer, default=0, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, approved, rejected
    language = Column(String, default="en", nullable=False)  # rw, en, fr, sw
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    
    def to_dict(self, include_user: bool = False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "media_url": self.media_url,
            "post_type": self.post_type,
            "likes_count": self.likes_count,
            "status": self.status,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_user and hasattr(self, 'user'):
            data["user"] = {
                "id": self.user.id,
                "display_name": self.user.display_name
            }
        return data
    
    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, status={self.status})>"

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")
    
    def to_dict(self, include_user: bool = False):
        data = {
            "id": self.id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_user and hasattr(self, 'user'):
            data["user"] = {
                "id": self.user.id,
                "display_name": self.user.display_name
            }
        return data
    
    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")
    
    def __repr__(self):
        return f"<Like(post_id={self.post_id}, user_id={self.user_id})>"
