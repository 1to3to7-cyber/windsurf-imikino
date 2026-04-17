from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from models.user import User
from schemas.auth import UserRegister, UserLogin, Token, PasswordReset, PasswordResetConfirm
from core.responses import success_response, error_response, validation_error_response
from db import get_db
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_user(user_data: UserRegister, db: Session):
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            return error_response("Email already registered", status_code=400)
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            display_name=user_data.display_name,
            role="user",
            xp=0,
            level=1,
            badges=[],
            is_active=True
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=new_user.id,
                action="user_register",
                resource_type="user",
                resource_id=new_user.id,
                details={"email": user_data.email, "display_name": user_data.display_name},
                success="success",
                db=db
            )
            
            logger.info(f"New user registered: {user_data.email}")
            return success_response(
                {
                    "id": new_user.id,
                    "email": new_user.email,
                    "display_name": new_user.display_name,
                    "role": new_user.role,
                    "xp": new_user.xp,
                    "level": new_user.level,
                    "badges": new_user.badges,
                    "created_at": new_user.created_at.isoformat() if new_user.created_at else None
                },
                message="User registered successfully"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering user: {str(e)}")
            return error_response("Registration failed", status_code=500)
    
    @staticmethod
    def authenticate_user(user_data: UserLogin, db: Session):
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            return error_response("Invalid credentials", status_code=401)
        
        if not user.is_active:
            return error_response("Account is inactive", status_code=401)
        
        if not verify_password(user_data.password, user.password_hash):
            return error_response("Invalid credentials", status_code=401)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        
        try:
            db.commit()
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=user.id,
                action="user_login",
                resource_type="user",
                resource_id=user.id,
                details={"email": user_data.email},
                success="success",
                db=db
            )
            
            logger.info(f"User authenticated: {user_data.email}")
            
            # Create tokens
            access_token_expires = timedelta(minutes=15)
            refresh_token_expires = timedelta(days=7)
            
            access_token = create_access_token(
                data={"sub": user.email, "role": user.role, "user_id": user.id},
                expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(
                data={"sub": user.email, "user_id": user.id}
            )
            
            return success_response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "display_name": user.display_name,
                        "role": user.role,
                        "xp": user.xp,
                        "level": user.level,
                        "badges": user.badges,
                        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
                    }
                },
                message="Login successful"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error authenticating user: {str(e)}")
            return error_response("Authentication failed", status_code=500)
    
    @staticmethod
    def refresh_token(refresh_token: str, db: Session):
        from core.security import verify_token
        try:
            payload = verify_token(refresh_token, token_type="refresh")
            user = db.query(User).filter(User.email == payload.get("sub")).first()
            if not user or not user.is_active:
                return error_response("Invalid refresh token", status_code=401)
            
            # Create new access token
            access_token_expires = timedelta(minutes=15)
            new_access_token = create_access_token(
                data={"sub": user.email, "role": user.role, "user_id": user.id},
                expires_delta=access_token_expires
            )
            
            return success_response(
                {
                    "access_token": new_access_token,
                    "token_type": "bearer"
                },
                message="Token refreshed successfully"
            )
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return error_response("Token refresh failed", status_code=401)
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response("User not found", status_code=404)
        
        if not verify_password(current_password, user.password_hash):
            return error_response("Current password is incorrect", status_code=400)
        
        try:
            user.password_hash = get_password_hash(new_password)
            db.commit()
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=user.id,
                action="password_change",
                resource_type="user",
                resource_id=user.id,
                success="success",
                db=db
            )
            
            logger.info(f"Password changed for user: {user.email}")
            return success_response(message="Password changed successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password: {str(e)}")
            return error_response("Password change failed", status_code=500)
    
    @staticmethod
    def initiate_password_reset(email: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return error_response("Email not found", status_code=404)
        
        try:
            # Generate reset token (simplified for MVP)
            reset_token = create_access_token(
                data={"sub": email, "type": "password_reset"},
                expires_delta=timedelta(hours=1)
            )
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=user.id,
                action="password_reset_request",
                resource_type="user",
                resource_id=user.id,
                details={"email": email},
                success="success",
                db=db
            )
            
            # MVP-SIMPLIFIED: In production, send email with reset link
            logger.info(f"Password reset requested for: {email}")
            return success_response(
                {
                    "reset_token": reset_token,
                    "expires_in": 3600  # 1 hour in seconds
                },
                message="Password reset token generated"
            )
        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return error_response("Password reset failed", status_code=500)
    
    @staticmethod
    def confirm_password_reset(reset_data: PasswordResetConfirm, db: Session):
        from core.security import verify_token
        try:
            payload = verify_token(reset_data.token)
            if payload.get("type") != "password_reset":
                return error_response("Invalid reset token", status_code=400)
            
            user = db.query(User).filter(User.email == payload.get("sub")).first()
            if not user:
                return error_response("User not found", status_code=404)
            
            # Update password
            user.password_hash = get_password_hash(reset_data.password)
            db.commit()
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=user.id,
                action="password_reset_confirm",
                resource_type="user",
                resource_id=user.id,
                success="success",
                db=db
            )
            
            logger.info(f"Password reset confirmed for user: {user.email}")
            return success_response(message="Password reset successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error confirming password reset: {str(e)}")
            return error_response("Password reset confirmation failed", status_code=500)
