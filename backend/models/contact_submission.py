from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ContactSubmission(Base):
    __tablename__ = "contact_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    user_data_snapshot = Column(JSON, nullable=True)  # User profile data at time of submission
    status = Column(String, default="new", nullable=False)  # new, in_progress, resolved, closed
    priority = Column(String, default="medium", nullable=False)  # low, medium, high, urgent
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin assigned to handle
    response = Column(Text, nullable=True)  # Admin response
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigned_admin = relationship("User", foreign_keys=[assigned_to])
    
    def to_dict(self, include_user: bool = False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "user_data_snapshot": self.user_data_snapshot or {},
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "response": self.response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_user and hasattr(self, 'user'):
            data["user"] = {
                "id": self.user.id,
                "display_name": self.user.display_name,
                "email": self.user.email
            }
        return data
    
    def __repr__(self):
        return f"<ContactSubmission(id={self.id}, name={self.name}, status={self.status})>"
