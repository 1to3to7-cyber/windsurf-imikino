from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    xp: int
    role: str
    badges: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class UserProgress(BaseModel):
    user_id: int
    course_id: int
    module_id: str
    completed: bool
    quiz_score: int

# Post Models
class PostCreate(BaseModel):
    content: str
    media_url: Optional[str] = None
    type: str = "text"

class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    media_url: Optional[str]
    type: str
    likes_count: int
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

# Course Models
class Module(BaseModel):
    id: str
    title: str
    type: str
    content: str

class CourseCreate(BaseModel):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    modules: List[Module]

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    thumbnail_url: Optional[str]
    modules: List[Module]
    created_at: datetime

    class Config:
        from_attributes = True

# Quiz Models
class Question(BaseModel):
    question: str
    options: List[str]
    type: str = "multiple_choice"

class QuizCreate(BaseModel):
    module_id: str
    questions: List[Question]
    correct_answers: List[int]

class QuizResponse(BaseModel):
    id: int
    module_id: str
    questions: List[Question]

    class Config:
        from_attributes = True

class QuizSubmission(BaseModel):
    answers: List[int]

# Task Models
class TaskCreate(BaseModel):
    title: str
    description: str
    xp_reward: int
    proof_type: str = "text"
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    xp_reward: int
    deadline: Optional[datetime]
    proof_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TaskSubmission(BaseModel):
    proof_content: str

class SubmissionResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    proof_content: str
    status: str
    created_at: datetime
    task: TaskResponse
    user: UserResponse

    class Config:
        from_attributes = True

# Auth Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Admin Models
class ModerationAction(BaseModel):
    action: str  # approve or reject
    reason: Optional[str] = None
