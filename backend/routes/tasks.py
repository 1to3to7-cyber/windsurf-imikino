from fastapi import APIRouter, Depends, HTTPException, status
from models import TaskResponse, TaskSubmission, SubmissionResponse
from auth import get_current_user, award_xp, check_and_award_badge
from db import db
import json

router = APIRouter()

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    """Get all tasks with user submission status."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks_rows = cursor.fetchall()
    
    tasks_list = []
    for row in tasks_rows:
        # Check if user has submitted this task
        cursor.execute('''
            SELECT id, status, created_at
            FROM submissions
            WHERE task_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (row["id"], current_user.id))
        
        submission_row = cursor.fetchone()
        
        tasks_list.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "xp_reward": row["xp_reward"],
            "deadline": row["deadline"],
            "proof_type": row["proof_type"],
            "status": row["status"],
            "created_at": row["created_at"],
            "user_submission": {
                "id": submission_row["id"],
                "status": submission_row["status"],
                "submitted_at": submission_row["created_at"]
            } if submission_row else None
        })
    
    conn.close()
    return tasks_list

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific task with user submission status."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task_row = cursor.fetchone()
    
    if not task_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has submitted this task
    cursor.execute('''
        SELECT id, status, proof_content, created_at
        FROM submissions
        WHERE task_id = ? AND user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (task_id, current_user.id))
    
    submission_row = cursor.fetchone()
    
    task_data = {
        "id": task_row["id"],
        "title": task_row["title"],
        "description": task_row["description"],
        "xp_reward": task_row["xp_reward"],
        "deadline": task_row["deadline"],
        "proof_type": task_row["proof_type"],
        "status": task_row["status"],
        "created_at": task_row["created_at"],
        "user_submission": {
            "id": submission_row["id"],
            "status": submission_row["status"],
            "proof_content": submission_row["proof_content"],
            "submitted_at": submission_row["created_at"]
        } if submission_row else None
    }
    
    conn.close()
    return task_data

@router.post("/{task_id}/claim")
async def claim_task(task_id: int, current_user: dict = Depends(get_current_user)):
    """Claim a task (mark as in progress)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task_row = cursor.fetchone()
    
    if not task_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user already submitted this task
    cursor.execute('''
        SELECT id FROM submissions
        WHERE task_id = ? AND user_id = ?
    ''', (task_id, current_user.id))
    
    existing_submission = cursor.fetchone()
    if existing_submission:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already submitted"
        )
    
    conn.close()
    
    return {"message": "Task claimed successfully", "task_id": task_id}

@router.post("/{task_id}/submit")
async def submit_task(task_id: int, submission: TaskSubmission, current_user: dict = Depends(get_current_user)):
    """Submit proof for a task."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task_row = cursor.fetchone()
    
    if not task_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user already submitted this task
    cursor.execute('''
        SELECT id FROM submissions
        WHERE task_id = ? AND user_id = ?
    ''', (task_id, current_user.id))
    
    existing_submission = cursor.fetchone()
    if existing_submission:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already submitted"
        )
    
    # Create submission
    cursor.execute('''
        INSERT INTO submissions (task_id, user_id, proof_content, status)
        VALUES (?, ?, ?, ?)
    ''', (task_id, current_user.id, submission.proof_content, "pending"))
    
    conn.commit()
    submission_id = cursor.lastrowid
    
    # Award XP for submitting task (pending approval)
    award_xp(current_user.id, 10)
    
    conn.close()
    
    return {
        "message": "Task submitted successfully",
        "submission_id": submission_id,
        "xp_awarded": 10,
        "pending_approval": True
    }

@router.get("/{task_id}/submissions", response_model=list[SubmissionResponse])
async def get_task_submissions(task_id: int, current_user: dict = Depends(get_current_user)):
    """Get all submissions for a task (admin only in real app, simplified for MVP)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task_row = cursor.fetchone()
    
    if not task_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get submissions with user info
    cursor.execute('''
        SELECT s.*, u.display_name, u.email, u.xp, u.role, u.badges, u.created_at as user_created_at
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        WHERE s.task_id = ?
        ORDER BY s.created_at DESC
    ''', (task_id,))
    
    submissions_rows = cursor.fetchall()
    conn.close()
    
    submissions_list = []
    for row in submissions_rows:
        user_info = {
            "id": row["user_id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "xp": row["xp"],
            "role": row["role"],
            "badges": eval(row["badges"]) if isinstance(row["badges"], str) else row["badges"],
            "created_at": row["user_created_at"]
        }
        
        submissions_list.append({
            "id": row["id"],
            "task_id": row["task_id"],
            "user_id": row["user_id"],
            "proof_content": row["proof_content"],
            "status": row["status"],
            "created_at": row["created_at"],
            "task": {
                "id": task_row["id"],
                "title": task_row["title"],
                "description": task_row["description"],
                "xp_reward": task_row["xp_reward"],
                "deadline": task_row["deadline"],
                "proof_type": task_row["proof_type"],
                "status": task_row["status"],
                "created_at": task_row["created_at"]
            },
            "user": user_info
        })
    
    return submissions_list
