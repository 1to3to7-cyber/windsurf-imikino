from fastapi import APIRouter, Depends, HTTPException, status
from models import UserResponse, UserProgress
from auth import get_current_user
from db import db

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.get("/me/progress")
async def get_user_progress(current_user: UserResponse = Depends(get_current_user)):
    """Get user's learning progress across all courses."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, c.title as course_title, m.title as module_title
        FROM progress p
        JOIN courses c ON p.course_id = c.id
        LEFT JOIN json_each(c.modules) as mod ON json_extract(mod.value, '$.id') = p.module_id
        LEFT JOIN json_each(c.modules) as m ON json_extract(m.value, '$.id') = p.module_id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
    ''', (current_user.id,))
    
    progress_rows = cursor.fetchall()
    conn.close()
    
    progress_list = []
    for row in progress_rows:
        progress_list.append({
            "user_id": row["user_id"],
            "course_id": row["course_id"],
            "module_id": row["module_id"],
            "completed": bool(row["completed"]),
            "quiz_score": row["quiz_score"],
            "course_title": row["course_title"],
            "module_title": row.get("module_title", "Unknown Module")
        })
    
    return {
        "user": current_user,
        "progress": progress_list,
        "total_courses_completed": len(set(p["course_id"] for p in progress_list if p["completed"]))
    }
