from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(..., min_length=1, max_length=2000, description="Task description")
    xp_reward: int = Field(..., gt=0, description="XP reward for completing task")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    proof_type: str = Field(default="text", description="Proof type (text, image, link)")
    priority: str = Field(default="medium", description="Task priority (low, medium, high)")
    category: Optional[str] = Field(None, max_length=50, description="Task category")
    max_submissions: Optional[int] = Field(None, gt=0, description="Maximum submissions allowed")
    
    @validator('proof_type')
    def validate_proof_type(cls, v):
        if v not in ['text', 'image', 'link']:
            raise ValueError('Proof type must be one of: text, image, link')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, min_length=1, max_length=2000, description="Task description")
    xp_reward: Optional[int] = Field(None, gt=0, description="XP reward for completing task")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    proof_type: Optional[str] = Field(None, description="Proof type")
    priority: Optional[str] = Field(None, description="Task priority")
    category: Optional[str] = Field(None, max_length=50, description="Task category")
    max_submissions: Optional[int] = Field(None, gt=0, description="Maximum submissions allowed")
    status: Optional[str] = Field(None, description="Task status (open, closed)")

class TaskResponse(BaseModel):
    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    xp_reward: int = Field(..., description="XP reward for completing task")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    proof_type: str = Field(..., description="Proof type")
    status: str = Field(..., description="Task status")
    priority: str = Field(..., description="Task priority")
    category: Optional[str] = Field(None, description="Task category")
    max_submissions: Optional[int] = Field(None, description="Maximum submissions allowed")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user_submission: Optional['SubmissionResponse'] = Field(None, description="User's submission if any")

class TaskList(BaseModel):
    tasks: List[TaskResponse] = Field(default=[], description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Tasks per page")

class SubmissionCreate(BaseModel):
    task_id: int = Field(..., description="Task ID")
    proof: str = Field(..., min_length=1, max_length=2000, description="Submission proof content")
    proof_url: Optional[str] = Field(None, description="Proof URL for image/link submissions")

class SubmissionUpdate(BaseModel):
    proof: Optional[str] = Field(None, min_length=1, max_length=2000, description="Submission proof content")
    proof_url: Optional[str] = Field(None, description="Proof URL for image/link submissions")

class SubmissionResponse(BaseModel):
    id: int = Field(..., description="Submission ID")
    task_id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="User ID")
    proof: str = Field(..., description="Submission proof content")
    proof_url: Optional[str] = Field(None, description="Proof URL")
    status: str = Field(..., description="Submission status")
    feedback: Optional[str] = Field(None, description="Admin feedback")
    reviewed_by: Optional[int] = Field(None, description="Admin reviewer ID")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user: Optional['UserResponse'] = Field(None, description="Submission author")
    task: Optional[TaskResponse] = Field(None, description="Related task")

class SubmissionModeration(BaseModel):
    status: str = Field(..., description="Moderation status (approved, rejected)")
    feedback: Optional[str] = Field(None, max_length=1000, description="Admin feedback")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError('Status must be approved or rejected')
        return v

class TaskClaim(BaseModel):
    task_id: int = Field(..., description="Task ID to claim")

class TaskStats(BaseModel):
    total_tasks: int = Field(default=0, description="Total tasks")
    open_tasks: int = Field(default=0, description="Open tasks")
    claimed_tasks: int = Field(default=0, description="Claimed tasks")
    completed_tasks: int = Field(default=0, description="Completed tasks")
    pending_submissions: int = Field(default=0, description="Pending submissions")
    total_xp_awarded: int = Field(default=0, description="Total XP awarded from tasks")
    average_completion_time: Optional[float] = Field(None, description="Average completion time in hours")
    top_categories: List[dict] = Field(default=[], description="Most popular task categories")

class TaskFilter(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status")
    priority: Optional[str] = Field(None, description="Filter by priority")
    category: Optional[str] = Field(None, description="Filter by category")
    proof_type: Optional[str] = Field(None, description="Filter by proof type")
    deadline_from: Optional[datetime] = Field(None, description="Filter tasks with deadline from date")
    deadline_to: Optional[datetime] = Field(None, description="Filter tasks with deadline to date")
    user_id: Optional[int] = Field(None, description="Filter by user")
