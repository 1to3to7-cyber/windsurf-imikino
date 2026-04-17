from fastapi import APIRouter, Depends, HTTPException, status
from models import PostCreate, PostResponse, CommentCreate, CommentResponse
from auth import get_current_user, award_xp
from db import db
import json

router = APIRouter()

@router.get("/", response_model=list[PostResponse])
async def get_posts():
    """Get all posts with user information."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, u.display_name, u.email, u.xp, u.role, u.badges, u.created_at as user_created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 50
    ''')
    
    posts_rows = cursor.fetchall()
    conn.close()
    
    posts_list = []
    for row in posts_rows:
        user_info = {
            "id": row["user_id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "xp": row["xp"],
            "role": row["role"],
            "badges": eval(row["badges"]) if isinstance(row["badges"], str) else row["badges"],
            "created_at": row["user_created_at"]
        }
        
        posts_list.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "content": row["content"],
            "media_url": row["media_url"],
            "type": row["type"],
            "likes_count": row["likes_count"],
            "created_at": row["created_at"],
            "user": user_info
        })
    
    return posts_list

@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    """Create a new post."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO posts (user_id, content, media_url, type)
        VALUES (?, ?, ?, ?)
    ''', (current_user.id, post.content, post.media_url, post.type))
    
    conn.commit()
    post_id = cursor.lastrowid
    
    # Get the created post with user info
    cursor.execute('''
        SELECT p.*, u.display_name, u.email, u.xp, u.role, u.badges, u.created_at as user_created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    ''', (post_id,))
    
    post_row = cursor.fetchone()
    conn.close()
    
    user_info = {
        "id": post_row["user_id"],
        "email": post_row["email"],
        "display_name": post_row["display_name"],
        "xp": post_row["xp"],
        "role": post_row["role"],
        "badges": eval(post_row["badges"]) if isinstance(post_row["badges"], str) else post_row["badges"],
        "created_at": post_row["user_created_at"]
    }
    
    # Award XP for creating post
    award_xp(current_user.id, 10)
    
    return {
        "id": post_row["id"],
        "user_id": post_row["user_id"],
        "content": post_row["content"],
        "media_url": post_row["media_url"],
        "type": post_row["type"],
        "likes_count": post_row["likes_count"],
        "created_at": post_row["created_at"],
        "user": user_info
    }

@router.post("/{post_id}/like")
async def like_post(post_id: int, current_user: dict = Depends(get_current_user)):
    """Like a post."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if already liked
    cursor.execute("SELECT * FROM likes WHERE post_id = ? AND user_id = ?", (post_id, current_user.id))
    existing_like = cursor.fetchone()
    
    if existing_like:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    # Add like
    cursor.execute('''
        INSERT INTO likes (post_id, user_id)
        VALUES (?, ?)
    ''', (post_id, current_user.id))
    
    # Update likes count
    cursor.execute("UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?", (post_id,))
    
    conn.commit()
    conn.close()
    
    # Award XP for liking
    award_xp(current_user.id, 5)
    
    return {"message": "Post liked successfully"}

@router.post("/{post_id}/comment", response_model=CommentResponse)
async def comment_post(post_id: int, comment: CommentCreate, current_user: dict = Depends(get_current_user)):
    """Comment on a post."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if post exists
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if not post:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create comment
    cursor.execute('''
        INSERT INTO comments (post_id, user_id, content)
        VALUES (?, ?, ?)
    ''', (post_id, current_user.id, comment.content))
    
    conn.commit()
    comment_id = cursor.lastrowid
    
    # Get the created comment with user info
    cursor.execute('''
        SELECT c.*, u.display_name, u.email, u.xp, u.role, u.badges, u.created_at as user_created_at
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    ''', (comment_id,))
    
    comment_row = cursor.fetchone()
    conn.close()
    
    user_info = {
        "id": comment_row["user_id"],
        "email": comment_row["email"],
        "display_name": comment_row["display_name"],
        "xp": comment_row["xp"],
        "role": comment_row["role"],
        "badges": eval(comment_row["badges"]) if isinstance(comment_row["badges"], str) else comment_row["badges"],
        "created_at": comment_row["user_created_at"]
    }
    
    # Award XP for commenting
    award_xp(current_user.id, 15)
    
    return {
        "id": comment_row["id"],
        "post_id": comment_row["post_id"],
        "user_id": comment_row["user_id"],
        "content": comment_row["content"],
        "created_at": comment_row["created_at"],
        "user": user_info
    }

@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_post_comments(post_id: int):
    """Get all comments for a post."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, u.display_name, u.email, u.xp, u.role, u.badges, u.created_at as user_created_at
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
    ''', (post_id,))
    
    comments_rows = cursor.fetchall()
    conn.close()
    
    comments_list = []
    for row in comments_rows:
        user_info = {
            "id": row["user_id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "xp": row["xp"],
            "role": row["role"],
            "badges": eval(row["badges"]) if isinstance(row["badges"], str) else row["badges"],
            "created_at": row["user_created_at"]
        }
        
        comments_list.append({
            "id": row["id"],
            "post_id": row["post_id"],
            "user_id": row["user_id"],
            "content": row["content"],
            "created_at": row["created_at"],
            "user": user_info
        })
    
    return comments_list
