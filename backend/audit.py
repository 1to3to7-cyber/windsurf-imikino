import logging
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
from models.audit_log import AuditLog
from db import get_db
from core.responses import success_response, error_response

logger = logging.getLogger(__name__)

class AuditLogService:
    @staticmethod
    def log_action(
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int],
        details: Optional[Dict[str, Any]],
        success: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None
    ) -> bool:
        try:
            if db is None:
                db = get_db()
            
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                created_at=datetime.utcnow()
            )
            
            db.add(audit_log)
            db.commit()
            
            logger.info(f"Audit log: {action} on {resource_type} {resource_id or ''} by user {user_id} - {success}")
            return True
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to log audit: {str(e)}")
            return False
    
    @staticmethod
    def log_auth_event(
        user_id: int,
        event: str,
        details: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None
    ) -> bool:
        return AuditLogService.log_action(
            user_id=user_id,
            action=event,
            resource_type="auth",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success="success",
            db=db
        )
    
    @staticmethod
    def log_user_action(
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int],
        details: Optional[Dict[str, Any]],
        db: Session = None
    ) -> bool:
        return AuditLogService.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            success="success",
            db=db
        )
    
    @staticmethod
    def log_admin_action(
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int],
        details: Optional[Dict[str, Any]],
        db: Session = None
    ) -> bool:
        return AuditLogService.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            success="success",
            db=db
        )
    
    @staticmethod
    def log_security_event(
        action: str,
        details: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None
    ) -> bool:
        return AuditLogService.log_action(
            user_id=None,
            action=action,
            resource_type="security",
            resource_id=None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success="success",
            db=db
        )
    
    @staticmethod
    def log_error(
        action: str,
        resource_type: str,
        resource_id: Optional[int],
        error_message: str,
        details: Optional[Dict[str, Any]],
        db: Session = None
    ) -> bool:
        return AuditLogService.log_action(
            user_id=None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details={
                **(details or {}),
                "error_message": error_message
            },
            ip_address=None,
            user_agent=None,
            success="failure",
            db=db
        )
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        success: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> list:
        try:
            query = db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            if success:
                query = query.filter(AuditLog.success == success)
            
            if date_from:
                query = query.filter(AuditLog.created_at >= date_from)
            
            if date_to:
                query = query.filter(AuditLog.created_at <= date_to)
            
            return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            return []
    
    @staticmethod
    def get_user_activity_summary(user_id: int, db: Session, days: int = 30) -> Dict[str, Any]:
        try:
            from datetime import timedelta
            
            date_since = datetime.utcnow() - timedelta(days=days)
            
            # Get recent activity
            logs = db.query(AuditLog).filter(
                AuditLog.user_id == user_id,
                AuditLog.created_at >= date_since,
                AuditLog.success == "success"
            ).all()
            
            # Count by action type
            auth_events = len([log for log in logs if log.resource_type == "auth"])
            post_events = len([log for log in logs if log.resource_type == "post"])
            task_events = len([log for log in logs if log.resource_type == "task"])
            course_events = len([log for log in logs if log.resource_type == "course"])
            
            return {
                "total_events": len(logs),
                "auth_events": auth_events,
                "post_events": post_events,
                "task_events": task_events,
                "course_events": course_events,
                "days_period": days,
                "date_since": date_since.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity summary: {str(e)}")
            return {}
    
    @staticmethod
    def get_security_summary(db: Session, hours: int = 24) -> Dict[str, Any]:
        try:
            from datetime import timedelta
            
            date_since = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent security events
            logs = db.query(AuditLog).filter(
                AuditLog.resource_type == "security",
                AuditLog.created_at >= date_since
            ).all()
            
            # Count by action
            failed_logins = len([log for log in logs if log.action == "login_failed"])
            successful_logins = len([log for log in logs if log.action == "login_success"])
            password_resets = len([log for log in logs if log.action == "password_reset_request"])
            suspicious_activities = len([log for log in logs if log.success == "failure"])
            
            return {
                "total_security_events": len(logs),
                "failed_logins": failed_logins,
                "successful_logins": successful_logins,
                "password_resets": password_resets,
                "suspicious_activities": suspicious_activities,
                "hours_period": hours,
                "date_since": date_since.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting security summary: {str(e)}")
            return {}
    
    @staticmethod
    def cleanup_old_logs(db: Session, days: int = 90) -> bool:
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old audit logs
            deleted_count = db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old audit logs older than {days} days")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up old audit logs: {str(e)}")
            return False
