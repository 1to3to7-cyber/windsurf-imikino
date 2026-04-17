from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
import os
from pydantic import BaseModel

from core.security import get_current_user
from models.user import User
from models.content import Content
from db import get_db
from audit import log_admin_action

router = APIRouter(prefix="/api/content", tags=["content"])
logger = logging.getLogger(__name__)

# Allowed file types for content upload
ALLOWED_FILE_TYPES = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "video": [".mp4", ".avi", ".mov", ".wmv"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".md"],
    "audio": [".mp3", ".wav", ".ogg"]
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class ContentSubmission(BaseModel):
    title: str
    description: str
    content_type: str  # post, article, video, image, document
    category: str = "general"
    tags: List[str] = []
    visibility: str = "public"  # public, private, unlisted
    social_sharing: Dict[str, Any] = {}

class ContentResponse(BaseModel):
    success: bool
    message: str
    content_id: Optional[int] = None

class SocialShare(BaseModel):
    platform: str  # facebook, twitter, instagram, linkedin, whatsapp
    url: str
    caption: Optional[str] = None
    hashtags: List[str] = []

def validate_file_upload(file: UploadFile) -> Dict[str, Any]:
    """Validate uploaded file and return file info"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Get file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Validate file type
    file_type = None
    for type_name, extensions in ALLOWED_FILE_TYPES.items():
        if file_ext in extensions:
            file_type = type_name
            break
    
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_ext} is not allowed"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    return {
        "filename": file.filename,
        "file_type": file_type,
        "file_size": file_size,
        "content_type": file.content_type
    }

def generate_social_share_url(content_id: int, platform: str) -> str:
    """Generate social sharing URLs for different platforms"""
    base_url = "https://imikino.rw"
    
    share_urls = {
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={base_url}/content/{content_id}",
        "twitter": f"https://twitter.com/intent/tweet?url={base_url}/content/{content_id}&text=Check out this content on Imikino",
        "instagram": f"https://www.instagram.com/",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={base_url}/content/{content_id}",
        "whatsapp": f"https://wa.me/?text={base_url}/content/{content_id}"
    }
    
    return share_urls.get(platform, base_url)

@router.post("/upload", response_model=ContentResponse)
async def upload_content(
    title: str,
    description: str,
    content_type: str,
    category: str = "general",
    tags: str = "",
    visibility: str = "public",
    social_sharing: str = "{}",
    file: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload user content with social media integration"""
    
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Parse social sharing settings
        social_settings = json.loads(social_sharing) if social_sharing else {}
        
        # Handle file upload
        file_info = None
        if file:
            file_info = validate_file_upload(file)
        
        # Insert content into database
        content_query = text("""
            INSERT INTO user_content (
                user_id, title, description, content_type, category,
                tags, visibility, social_sharing, file_url, thumbnail_url,
                status, moderation_status, created_at, updated_at
            ) VALUES (
                :user_id, :title, :description, :content_type, :category,
                :tags, :visibility, :social_sharing, :file_url, :thumbnail_url,
                'draft', 'pending', NOW(), NOW()
            )
        """)
        
        db.execute(content_query, {
            "user_id": current_user.id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "category": category,
            "tags": json.dumps(tag_list),
            "visibility": visibility,
            "social_sharing": social_settings,
            "file_url": file_info["filename"] if file_info else None,
            "thumbnail_url": None  # TODO: Generate thumbnail for images/videos
        })
        
        db.commit()
        
        # Get the content ID
        content_id = db.execute(text("SELECT last_insert_rowid()")).scalar()
        
        # Handle social media sharing
        if social_settings:
            for platform, settings in social_settings.items():
                share_url = generate_social_share_url(content_id, platform)
                # TODO: Actually post to social media APIs
                logger.info(f"Social share to {platform}: {share_url}")
        
        # Log the action
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="content_upload",
            resource="content",
            resource_id=content_id,
            details=json.dumps({
                "title": title,
                "content_type": content_type,
                "category": category,
                "file_uploaded": bool(file_info),
                "social_sharing_enabled": bool(social_settings),
                "tags": tag_list
            })
        )
        
        return ContentResponse(
            success=True,
            message="Content uploaded successfully",
            content_id=content_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload content"
        )

@router.get("/my-content")
async def get_user_content(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's uploaded content"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        content_query = text("""
            SELECT id, title, description, content_type, category, tags, visibility,
                   file_url, thumbnail_url, likes_count, shares_count, views_count,
                   comments_count, featured, status, created_at, updated_at
            FROM user_content 
            WHERE user_id = :user_id AND status = 'published'
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        results = db.execute(content_query, {
            "user_id": current_user.id,
            "skip": skip,
            "limit": limit
        }).fetchall()
        
        content_list = []
        for result in results:
            content_list.append({
                "id": result.id,
                "title": result.title,
                "description": result.description,
                "content_type": result.content_type,
                "category": result.category,
                "tags": json.loads(result.tags) if result.tags else [],
                "visibility": result.visibility,
                "file_url": result.file_url,
                "thumbnail_url": result.thumbnail_url,
                "likes_count": result.likes_count,
                "shares_count": result.shares_count,
                "views_count": result.views_count,
                "comments_count": result.comments_count,
                "featured": result.featured,
                "status": result.status,
                "created_at": result.created_at,
                "updated_at": result.updated_at
            })
        
        return {
            "content": content_list,
            "total": len(content_list),
            "has_more": len(content_list) == limit
        }
        
    except Exception as e:
        logger.error(f"Error getting user content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )

@router.get("/featured")
async def get_featured_content(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get featured content from all users"""
    
    try:
        featured_query = text("""
            SELECT c.id, c.title, c.description, c.content_type, c.category,
                   c.tags, c.file_url, c.thumbnail_url, c.likes_count,
                   c.shares_count, c.views_count, c.comments_count,
                   u.display_name as author_name, u.avatar_url as author_avatar,
                   c.created_at, c.updated_at
            FROM user_content c
            JOIN users u ON c.user_id = u.id
            WHERE c.featured = true AND c.status = 'published'
            ORDER BY c.created_at DESC
            LIMIT :limit
        """)
        
        results = db.execute(featured_query, {"limit": limit}).fetchall()
        
        featured_content = []
        for result in results:
            featured_content.append({
                "id": result.id,
                "title": result.title,
                "description": result.description,
                "content_type": result.content_type,
                "category": result.category,
                "tags": json.loads(result.tags) if result.tags else [],
                "file_url": result.file_url,
                "thumbnail_url": result.thumbnail_url,
                "likes_count": result.likes_count,
                "shares_count": result.shares_count,
                "views_count": result.views_count,
                "comments_count": result.comments_count,
                "author": {
                    "name": result.author_name,
                    "avatar": result.author_avatar
                },
                "created_at": result.created_at,
                "updated_at": result.updated_at
            })
        
        return featured_content
        
    except Exception as e:
        logger.error(f"Error getting featured content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve featured content"
        )

@router.post("/{content_id}/like")
async def like_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Like content and update engagement metrics"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # Check if user already liked this content
        like_check_query = text("""
            SELECT COUNT(*) as liked_count
            FROM content_likes
            WHERE user_id = :user_id AND content_id = :content_id
        """)
        
        result = db.execute(like_check_query, {
            "user_id": current_user.id,
            "content_id": content_id
        }).fetchone()
        
        if result.liked_count > 0:
            return {"message": "Content already liked"}
        
        # Add like
        like_query = text("""
            INSERT INTO content_likes (user_id, content_id, created_at)
            VALUES (:user_id, :content_id, NOW())
        """)
        
        db.execute(like_query, {
            "user_id": current_user.id,
            "content_id": content_id
        })
        
        # Update content likes count
        update_query = text("""
            UPDATE user_content 
            SET likes_count = likes_count + 1
            WHERE id = :content_id
        """)
        
        db.execute(update_query, {"content_id": content_id})
        db.commit()
        
        # Log action
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="content_like",
            resource="content",
            resource_id=content_id
        )
        
        return {"message": "Content liked successfully"}
        
    except Exception as e:
        logger.error(f"Error liking content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like content"
        )

@router.get("/categories")
async def get_content_categories():
    """Get available content categories"""
    categories = [
        {"value": "general", "label": "General"},
        {"value": "educational", "label": "Educational"},
        {"value": "entertainment", "label": "Entertainment"},
        {"value": "sports", "label": "Sports"},
        {"value": "technology", "label": "Technology"},
        {"value": "lifestyle", "label": "Lifestyle"},
        {"value": "business", "label": "Business"}
    ]
    return categories
