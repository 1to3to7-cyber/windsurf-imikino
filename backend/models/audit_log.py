from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True)  # user, post, course, task, etc.
    resource_id = Column(Integer, nullable=True, index=True)
    details = Column(JSON, nullable=True)  # Additional context about the action
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    success = Column(String, nullable=False)  # success, failure, error
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def to_dict(self, include_user: bool = False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details or {},
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_user and hasattr(self, 'user'):
            data["user"] = {
                "id": self.user.id,
                "email": self.user.email
            }
        return data
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action}, success={self.success})>"
