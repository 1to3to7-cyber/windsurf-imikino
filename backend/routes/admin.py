from fastapi import APIRouter, Depends, HTTPException, status
from models import ModerationAction, SubmissionResponse
from auth import get_current_admin_user, award_xp, check_and_award_badge
from db import db
import json

router = APIRouter()

@router.get("/submissions", response_model=list[SubmissionResponse])
async def get_pending_submissions(current_user: dict = Depends(get_current_admin_user)):
    """Get all pending task submissions for review."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, t.title as task_title, t.xp_reward as task_xp, u.display_name, u.email, u.xp, u.role, u.badges, u.created_at as user_created_at
        FROM submissions s
        JOIN tasks t ON s.task_id = t.id
        JOIN users u ON s.user_id = u.id
        WHERE s.status = 'pending'
        ORDER BY s.created_at ASC
    ''')
    
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
                "id": row["task_id"],
                "title": row["task_title"],
                "xp_reward": row["task_xp"]
            },
            "user": user_info
        })
    
    return submissions_list

@router.post("/submissions/{submission_id}/moderate")
async def moderate_submission(submission_id: int, action: ModerationAction, current_user: dict = Depends(get_current_admin_user)):
    """Approve or reject a task submission."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get submission with task info
    cursor.execute('''
        SELECT s.*, t.xp_reward
        FROM submissions s
        JOIN tasks t ON s.task_id = t.id
        WHERE s.id = ?
    ''', (submission_id,))
    
    submission_row = cursor.fetchone()
    
    if not submission_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    if submission_row["status"] != "pending":
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission already moderated"
        )
    
    # Update submission status
    new_status = action.action
    cursor.execute('''
        UPDATE submissions
        SET status = ?
        WHERE id = ?
    ''', (new_status, submission_id))
    
    # Award additional XP if approved
    xp_awarded = 0
    if new_status == "approved":
        xp_awarded = submission_row["xp_reward"]  # Full task XP reward
        award_xp(submission_row["user_id"], xp_awarded)
        
        # Check for task completion badges
        cursor.execute('''
            SELECT COUNT(*) as completed_tasks
            FROM submissions
            WHERE user_id = ? AND status = 'approved'
        ''', (submission_row["user_id"]))
        
        task_count = cursor.fetchone()["completed_tasks"]
        if task_count >= 1:
            check_and_award_badge(submission_row["user_id"], "task_starter")
        if task_count >= 5:
            check_and_award_badge(submission_row["user_id"], "task_achiever")
        if task_count >= 10:
            check_and_award_badge(submission_row["user_id"], "task_master")
    
    conn.commit()
    conn.close()
    
    return {
        "message": f"Submission {new_status} successfully",
        "submission_id": submission_id,
        "xp_awarded": xp_awarded,
        "action": new_status
    }

@router.get("/posts")
async def get_pending_posts(current_user: dict = Depends(get_current_admin_user)):
    """Get posts that need moderation (simplified MVP - returns all posts)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, u.display_name, u.email
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 100
    ''')
    
    posts_rows = cursor.fetchall()
    conn.close()
    
    posts_list = []
    for row in posts_rows:
        posts_list.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "content": row["content"],
            "media_url": row["media_url"],
            "type": row["type"],
            "likes_count": row["likes_count"],
            "created_at": row["created_at"],
            "user": {
                "id": row["user_id"],
                "display_name": row["display_name"],
                "email": row["email"]
            }
        })
    
    return posts_list

@router.post("/posts/{post_id}/moderate")
async def moderate_post(post_id: int, action: ModerationAction, current_user: dict = Depends(get_current_admin_user)):
    """Approve or reject a post (simplified MVP - just returns success)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if post exists
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post_row = cursor.fetchone()
    
    if not post_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # In a real app, you might hide posts or take other moderation actions
    # For MVP, we'll just return success
    conn.close()
    
    return {
        "message": f"Post moderation action '{action.action}' completed",
        "post_id": post_id,
        "action": action.action,
        "reason": action.reason
    }

@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_admin_user)):
    """Get all users for admin dashboard."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.*,
               COUNT(DISTINCT s.id) as completed_tasks,
               COUNT(DISTINCT p.id) as created_posts
        FROM users u
        LEFT JOIN submissions s ON u.id = s.user_id AND s.status = 'approved'
        LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    
    users_rows = cursor.fetchall()
    conn.close()
    
    users_list = []
    for row in users_rows:
        users_list.append({
            "id": row["id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "xp": row["xp"],
            "role": row["role"],
            "badges": eval(row["badges"]) if isinstance(row["badges"], str) else row["badges"],
            "created_at": row["created_at"],
            "stats": {
                "completed_tasks": row["completed_tasks"],
                "created_posts": row["created_posts"]
            }
        })
    
    return users_list

@router.post("/users/{user_id}/toggle-role")
async def toggle_user_role(user_id: int, current_user: dict = Depends(get_current_admin_user)):
    """Toggle user role between user and admin."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get current user role
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Toggle role
    new_role = "admin" if user_row["role"] == "user" else "user"
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    
    conn.commit()
    conn.close()
    
    return {
        "message": f"User role updated to {new_role}",
        "user_id": user_id,
        "new_role": new_role
    }

@router.get("/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(get_current_admin_user)):
    """Get admin dashboard statistics."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get various stats
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()["total_users"]
    
    cursor.execute("SELECT COUNT(*) as pending_submissions FROM submissions WHERE status = 'pending'")
    pending_submissions = cursor.fetchone()["pending_submissions"]
    
    cursor.execute("SELECT COUNT(*) as total_posts FROM posts")
    total_posts = cursor.fetchone()["total_posts"]
    
    cursor.execute("SELECT COUNT(*) as total_tasks FROM tasks")
    total_tasks = cursor.fetchone()["total_tasks"]
    
    cursor.execute('''
        SELECT COUNT(*) as completed_tasks
        FROM submissions
        WHERE status = 'approved'
    ''')
    completed_tasks = cursor.fetchone()["completed_tasks"]
    
    conn.close()
    
    return {
        "stats": {
            "total_users": total_users,
            "pending_submissions": pending_submissions,
            "total_posts": total_posts,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks
        },
        "admin": current_user
    }
