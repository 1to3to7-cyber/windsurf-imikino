from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    thumbnail = Column(String, nullable=True)
    xp_reward = Column(Integer, nullable=False)
    status = Column(String, default="active", nullable=False)  # active, inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="course", cascade="all, delete-orphan")
    
    def to_dict(self, include_modules: bool = False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "xp_reward": self.xp_reward,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_modules and hasattr(self, 'modules'):
            data["modules"] = [module.to_dict() for module in self.modules]
        return data
    
    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title}, status={self.status})>"

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String, default="text", nullable=False)  # text, video, quiz
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    quiz = relationship("Quiz", back_populates="module", uselist=False, cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="module", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "order_index": self.order_index,
            "title": self.title,
            "content": self.content,
            "type": self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Module(id={self.id}, course_id={self.course_id}, type={self.type})>"

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    questions = Column(JSON, nullable=False)  # List of question objects
    answers = Column(JSON, nullable=False)  # List of correct answer indices
    xp_reward = Column(Integer, nullable=False)
    passing_score = Column(Integer, default=70, nullable=False)  # Minimum percentage to pass
    time_limit = Column(Integer, nullable=True)  # Minutes, optional
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="quiz")
    
    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "questions": self.questions or [],
            "answers": self.answers or [],
            "xp_reward": self.xp_reward,
            "passing_score": self.passing_score,
            "time_limit": self.time_limit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, module_id={self.module_id}, xp_reward={self.xp_reward})>"

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    module_index = Column(Integer, nullable=False)
    completed = Column(Integer, default=0, nullable=False)  # 0 or 1
    quiz_score = Column(Integer, default=0, nullable=False)  # Percentage score
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    course = relationship("Course", back_populates="progress")
    module = relationship("Module", back_populates="progress")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "module_id": self.module_id,
            "module_index": self.module_index,
            "completed": self.completed,
            "quiz_score": self.quiz_score,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, course_id={self.course_id}, completed={self.completed})>"
