from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Course title")
    description: str = Field(..., min_length=1, max_length=2000, description="Course description")
    thumbnail: Optional[str] = Field(None, description="Course thumbnail URL")
    xp_reward: int = Field(..., gt=0, description="XP reward for completing course")

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Course title")
    description: Optional[str] = Field(None, min_length=1, max_length=2000, description="Course description")
    thumbnail: Optional[str] = Field(None, description="Course thumbnail URL")
    xp_reward: Optional[int] = Field(None, gt=0, description="XP reward for completing course")
    status: Optional[str] = Field(None, description="Course status (active, inactive)")

class CourseResponse(BaseModel):
    id: int = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    thumbnail: Optional[str] = Field(None, description="Course thumbnail URL")
    xp_reward: int = Field(..., description="XP reward for completing course")
    status: str = Field(..., description="Course status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    modules: Optional[List['ModuleResponse']] = Field([], description="Course modules")
    progress: Optional['ProgressResponse']] = Field([], description="User progress")

class ModuleCreate(BaseModel):
    course_id: int = Field(..., description="Course ID")
    order_index: int = Field(..., gt=0, description="Module order in course")
    title: str = Field(..., min_length=1, max_length=200, description="Module title")
    content: str = Field(..., min_length=1, max_length=5000, description="Module content")
    type: str = Field(default="text", description="Module type (text, video, quiz)")
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['text', 'video', 'quiz']:
            raise ValueError('Module type must be one of: text, video, quiz')
        return v

class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Module title")
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="Module content")
    type: Optional[str] = Field(None, description="Module type")
    order_index: Optional[int] = Field(None, gt=0, description="Module order in course")

class ModuleResponse(BaseModel):
    id: int = Field(..., description="Module ID")
    course_id: int = Field(..., description="Course ID")
    order_index: int = Field(..., description="Module order in course")
    title: str = Field(..., description="Module title")
    content: str = Field(..., description="Module content")
    type: str = Field(..., description="Module type")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    quiz: Optional['QuizResponse'] = Field(None, description="Quiz for this module")
    progress: Optional['ProgressResponse'] = Field(None, description="User progress")

class QuizCreate(BaseModel):
    module_id: int = Field(..., description="Module ID")
    questions: List[dict] = Field(..., min_items=1, description="Quiz questions")
    answers: List[int] = Field(..., min_items=1, description="Correct answer indices")
    xp_reward: int = Field(..., gt=0, description="XP reward for passing quiz")
    passing_score: int = Field(default=70, ge=50, le=100, description="Minimum percentage to pass")
    time_limit: Optional[int] = Field(None, gt=0, description="Time limit in minutes")

class QuizUpdate(BaseModel):
    questions: Optional[List[dict]] = Field(None, min_items=1, description="Quiz questions")
    answers: Optional[List[int]] = Field(None, min_items=1, description="Correct answer indices")
    xp_reward: Optional[int] = Field(None, gt=0, description="XP reward for passing quiz")
    passing_score: Optional[int] = Field(None, ge=50, le=100, description="Minimum percentage to pass")
    time_limit: Optional[int] = Field(None, gt=0, description="Time limit in minutes")

class QuizResponse(BaseModel):
    id: int = Field(..., description="Quiz ID")
    module_id: int = Field(..., description="Module ID")
    questions: List[dict] = Field(..., description="Quiz questions")
    answers: List[int] = Field(..., description="Correct answer indices")
    xp_reward: int = Field(..., description="XP reward for passing quiz")
    passing_score: int = Field(..., description="Minimum percentage to pass")
    time_limit: Optional[int] = Field(None, description="Time limit in minutes")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

class QuizSubmission(BaseModel):
    answers: List[int] = Field(..., min_items=1, description="User's quiz answers")

class QuizResult(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Quiz score percentage")
    passed: bool = Field(..., description="Whether user passed the quiz")
    xp_awarded: int = Field(..., ge=0, description="XP awarded for this quiz")
    correct_answers: int = Field(..., ge=0, description="Number of correct answers")
    total_questions: int = Field(..., gt=0, description="Total number of questions")

class ProgressResponse(BaseModel):
    id: int = Field(..., description="Progress ID")
    user_id: int = Field(..., description="User ID")
    course_id: int = Field(..., description="Course ID")
    module_id: int = Field(..., description="Module ID")
    module_index: int = Field(..., description="Module order in course")
    completed: int = Field(..., description="Completion status (0 or 1)")
    quiz_score: int = Field(..., description="Quiz score percentage")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

class CourseList(BaseModel):
    courses: List[CourseResponse] = Field(default=[], description="List of courses")
    total: int = Field(..., description="Total number of courses")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Courses per page")

class CourseStats(BaseModel):
    total_courses: int = Field(default=0, description="Total courses")
    active_courses: int = Field(default=0, description="Active courses")
    completed_courses: int = Field(default=0, description="Completed courses")
    in_progress_courses: int = Field(default=0, description="Courses in progress")
    total_xp_awarded: int = Field(default=0, description="Total XP awarded from courses")
    average_completion_rate: float = Field(default=0.0, description="Average completion rate")
