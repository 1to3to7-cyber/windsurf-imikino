from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    xp_reward = Column(Integer, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    proof_type = Column(String, default="text", nullable=False)  # text, image, link
    status = Column(String, default="open", nullable=False)  # open, closed
    priority = Column(String, default="medium", nullable=False)  # low, medium, high
    category = Column(String, nullable=True)  # Optional categorization
    max_submissions = Column(Integer, nullable=True)  # Optional limit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    submissions = relationship("Submission", back_populates="task", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "xp_reward": self.xp_reward,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "proof_type": self.proof_type,
            "status": self.status,
            "priority": self.priority,
            "category": self.category,
            "max_submissions": self.max_submissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    proof = Column(Text, nullable=False)
    proof_url = Column(String, nullable=True)  # For image/link submissions
    status = Column(String, default="pending", nullable=False)  # pending, approved, rejected
    feedback = Column(Text, nullable=True)  # Admin feedback
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="submissions")
    user = relationship("User", foreign_keys=[user_id], back_populates="submissions")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def to_dict(self, include_user: bool = False, include_task: bool = False):
        data = {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "proof": self.proof,
            "proof_url": self.proof_url,
            "status": self.status,
            "feedback": self.feedback,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_user and hasattr(self, 'user'):
            data["user"] = {
                "id": self.user.id,
                "display_name": self.user.display_name
            }
        if include_task and hasattr(self, 'task'):
            data["task"] = self.task.to_dict()
        return data
    
    def __repr__(self):
        return f"<Submission(id={self.id}, task_id={self.task_id}, user_id={self.user_id}, status={self.status})>"
