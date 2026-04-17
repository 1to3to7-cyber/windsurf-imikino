from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from models.post import Post, Comment
from models.submission import Submission
from models.user import User
from core.responses import success_response, error_response
from db import get_db

logger = logging.getLogger(__name__)

class ModerationService:
    @staticmethod
    def moderate_post(post_id: int, status: str, reason: Optional[str], moderator_id: int, db: Session) -> bool:
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return False
            
            # Update post status
            post.status = status
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=moderator_id,
                action="post_moderate",
                resource_type="post",
                resource_id=post_id,
                details={
                    "old_status": post.status,
                    "new_status": status,
                    "reason": reason
                },
                success="success",
                db=db
            )
            
            db.commit()
            
            # Notify post author if rejected
            if status == "rejected" and reason:
                # MVP-SIMPLIFIED: Send notification email
                logger.info(f"Post {post_id} rejected. Reason: {reason}")
            
            logger.info(f"Post {post_id} moderated to {status} by moderator {moderator_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error moderating post: {str(e)}")
            return False
    
    @staticmethod
    def moderate_comment(comment_id: int, action: str, moderator_id: int, db: Session) -> bool:
        try:
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return False
            
            if action == "delete":
                # Soft delete comment
                comment.deleted_at = datetime.utcnow()
                
                # Log audit
                from audit import AuditLogService
                AuditLogService.log_action(
                    user_id=moderator_id,
                    action="comment_delete",
                    resource_type="comment",
                    resource_id=comment_id,
                    details={
                        "post_id": comment.post_id,
                        "user_id": comment.user_id
                    },
                    success="success",
                    db=db
                )
                
                db.commit()
                logger.info(f"Comment {comment_id} deleted by moderator {moderator_id}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error moderating comment: {str(e)}")
            return False
    
    @staticmethod
    def review_submission(submission_id: int, status: str, feedback: Optional[str], reviewer_id: int, db: Session) -> bool:
        try:
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            if not submission:
                return False
            
            # Update submission status
            old_status = submission.status
            submission.status = status
            submission.feedback = feedback
            submission.reviewed_by = reviewer_id
            submission.reviewed_at = datetime.utcnow()
            
            # Award XP if approved
            if status == "approved" and old_status != "approved":
                from services.xp_service import XPService
                xp_awarded = XPService.award_xp(
                    user_id=submission.user_id,
                    xp_amount=submission.task.xp_reward if hasattr(submission, 'task') else 0,
                    reason="task_completion",
                    db=db
                )
                
                if not xp_awarded:
                    logger.error(f"Failed to award XP for approved submission {submission_id}")
                    return False
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=reviewer_id,
                action="submission_review",
                resource_type="submission",
                resource_id=submission_id,
                details={
                    "old_status": old_status,
                    "new_status": status,
                    "feedback": feedback,
                    "xp_awarded": submission.task.xp_reward if status == "approved" and hasattr(submission, 'task') else 0
                },
                success="success",
                db=db
            )
            
            db.commit()
            
            # Notify user of decision
            if feedback and status in ["approved", "rejected"]:
                # MVP-SIMPLIFIED: Send notification email
                logger.info(f"Submission {submission_id} {status}. Feedback: {feedback}")
            
            logger.info(f"Submission {submission_id} reviewed to {status} by reviewer {reviewer_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error reviewing submission: {str(e)}")
            return False
    
    @staticmethod
    def get_pending_posts(db: Session, limit: int = 50) -> List[Post]:
        try:
            return db.query(Post).filter(
                Post.status == "pending",
                Post.deleted_at.is_(None)
            ).order_by(Post.created_at).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting pending posts: {str(e)}")
            return []
    
    @staticmethod
    def get_pending_submissions(db: Session, limit: int = 50) -> List[Submission]:
        try:
            return db.query(Submission).filter(
                Submission.status == "pending",
                Submission.deleted_at.is_(None)
            ).order_by(Submission.created_at).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting pending submissions: {str(e)}")
            return []
    
    @staticmethod
    def bulk_moderate_posts(post_ids: List[int], status: str, reason: Optional[str], moderator_id: int, db: Session) -> dict:
        results = {"success": 0, "failed": 0, "errors": []}
        
        try:
            for post_id in post_ids:
                post = db.query(Post).filter(Post.id == post_id).first()
                if post:
                    post.status = status
                    
                    # Log audit for each post
                    from audit import AuditLogService
                    AuditLogService.log_action(
                        user_id=moderator_id,
                        action="post_moderate",
                        resource_type="post",
                        resource_id=post_id,
                        details={
                            "old_status": post.status,
                            "new_status": status,
                            "reason": reason
                        },
                        success="success",
                        db=db
                    )
                    
                    results["success"] += 1
            
            db.commit()
            logger.info(f"Bulk moderated {results['success']} posts to {status} by moderator {moderator_id}")
            
        except Exception as e:
            db.rollback()
            error_msg = f"Error in bulk moderation: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    @staticmethod
    def bulk_review_submissions(submission_ids: List[int], status: str, feedback: Optional[str], reviewer_id: int, db: Session) -> dict:
        results = {"success": 0, "failed": 0, "errors": []}
        
        try:
            from services.xp_service import XPService
            
            for submission_id in submission_ids:
                submission = db.query(Submission).filter(Submission.id == submission_id).first()
                if submission:
                    old_status = submission.status
                    submission.status = status
                    submission.feedback = feedback
                    submission.reviewed_by = reviewer_id
                    submission.reviewed_at = datetime.utcnow()
                    
                    # Award XP if approved
                    if status == "approved" and old_status != "approved":
                        xp_awarded = XPService.award_xp(
                            user_id=submission.user_id,
                            xp_amount=submission.task.xp_reward if hasattr(submission, 'task') else 0,
                            reason="task_completion",
                            db=db
                        )
                        
                        if not xp_awarded:
                            results["errors"].append(f"Failed to award XP for submission {submission_id}")
                    
                    # Log audit for each submission
                    from audit import AuditLogService
                    AuditLogService.log_action(
                        user_id=reviewer_id,
                        action="submission_review",
                        resource_type="submission",
                        resource_id=submission_id,
                        details={
                            "old_status": old_status,
                            "new_status": status,
                            "feedback": feedback,
                            "xp_awarded": submission.task.xp_reward if status == "approved" and hasattr(submission, 'task') else 0
                        },
                        success="success",
                        db=db
                    )
                    
                    results["success"] += 1
            
            db.commit()
            logger.info(f"Bulk reviewed {results['success']} submissions to {status} by reviewer {reviewer_id}")
            
        except Exception as e:
            db.rollback()
            error_msg = f"Error in bulk review: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results
