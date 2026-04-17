from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class AISkill(Base):
    __tablename__ = "ai_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    query_pattern = Column(String(255), nullable=False, index=True)  # First 100 chars as pattern
    language = Column(String(10), nullable=False, index=True)  # rw, en, fr, sw
    source_types_used = Column(String(100), nullable=False)  # course,task,post,profile
    confidence_score = Column(Float, default=0.0, nullable=False)
    usage_count = Column(Integer, default=1, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Learning metadata
    learning_context = Column(Text, nullable=True)  # JSON string of context
    user_feedback = Column(JSON, nullable=True)  # User feedback on responses
    skill_category = Column(String(50), nullable=False)  # academic, technical, social
    
    def to_dict(self):
        return {
            "id": self.id,
            "query_pattern": self.query_pattern,
            "language": self.language,
            "source_types_used": self.source_types_used,
            "confidence_score": self.confidence_score,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "learning_context": self.learning_context,
            "user_feedback": self.user_feedback,
            "skill_category": self.skill_category
        }
    
    def __repr__(self):
        return f"<AISkill(id={self.id}, pattern={self.query_pattern[:50]}..., lang={self.language})>"
