from sqlalchemy.orm import Session
from typing import Optional
import logging
from models.user import User
from models.progress import Progress
from models.submission import Submission
from core.responses import success_response, error_response

logger = logging.getLogger(__name__)

class XPService:
    # XP thresholds for levels
    LEVEL_THRESHOLDS = [
        {"level": 1, "min_xp": 0, "max_xp": 99, "title": "Beginner"},
        {"level": 2, "min_xp": 100, "max_xp": 299, "title": "Novice"},
        {"level": 3, "min_xp": 300, "max_xp": 699, "title": "Intermediate"},
        {"level": 4, "min_xp": 700, "max_xp": 1499, "title": "Advanced"},
        {"level": 5, "min_xp": 1500, "max_xp": 2999, "title": "Expert"},
        {"level": 6, "min_xp": 3000, "max_xp": 5999, "title": "Master"},
        {"level": 7, "min_xp": 6000, "max_xp": 9999, "title": "Legend"},
        {"level": 8, "min_xp": 10000, "max_xp": 19999, "title": "Champion"},
        {"level": 9, "min_xp": 20000, "max_xp": 39999, "title": "Master"},
        {"level": 10, "min_xp": 40000, "max_xp": float('inf'), "title": "Grandmaster"}
    ]
    
    # Badge definitions
    BADGES = [
        {
            "id": "first_post",
            "name": "First Steps",
            "description": "Created your first post",
            "icon": "👣",
            "xp_required": 0
        },
        {
            "id": "course_complete",
            "name": "Course Graduate",
            "description": "Completed your first course",
            "icon": "🎓",
            "xp_required": 50
        },
        {
            "id": "task_complete",
            "name": "Task Master",
            "description": "Completed your first task",
            "icon": "✅",
            "xp_required": 15
        },
        {
            "id": "social_butterfly",
            "name": "Social Butterfly",
            "description": "Received 10 likes on your posts",
            "icon": "🦋",
            "xp_required": 0
        },
        {
            "id": "helper",
            "name": "Community Helper",
            "description": "Helped 5 other users",
            "icon": "🤝",
            "xp_required": 0
        },
        {
            "id": "streak_warrior",
            "name": "Streak Warrior",
            "description": "7-day login streak",
            "icon": "🔥",
            "xp_required": 0
        },
        {
            "id": "quiz_master",
            "name": "Quiz Master",
            "description": "Scored 100% on 5 quizzes",
            "icon": "🧠",
            "xp_required": 0
        },
        {
            "id": "task_champion",
            "name": "Task Champion",
            "description": "Completed 10 tasks",
            "icon": "🏆",
            "xp_required": 0
        },
        {
            "id": "level_10",
            "name": "Elite",
            "description": "Reached level 10",
            "icon": "⭐",
            "xp_required": 40000
        }
    ]
    
    @staticmethod
    def calculate_level(xp: int) -> dict:
        for threshold in reversed(XPService.LEVEL_THRESHOLDS):
            if xp >= threshold["min_xp"]:
                return threshold
        return XPService.LEVEL_THRESHOLDS[0]  # Default to level 1
    
    @staticmethod
    def award_xp(user_id: int, xp_amount: int, reason: str, db: Session) -> bool:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User not found for XP award: {user_id}")
                return False
            
            old_xp = user.xp
            old_level = user.level
            
            # Update user XP
            user.xp += xp_amount
            
            # Calculate new level
            new_level_info = XPService.calculate_level(user.xp)
            user.level = new_level_info["level"]
            
            # Check for new badges
            new_badges = user.badges.copy() if user.badges else []
            earned_badges = XPService.check_badge_earnings(user, old_xp, user.xp, db)
            
            for badge in earned_badges:
                if badge["id"] not in [b["id"] for b in new_badges]:
                    new_badges.append(badge)
            
            user.badges = new_badges
            
            db.commit()
            
            # Log audit
            from audit import AuditLogService
            AuditLogService.log_action(
                user_id=user_id,
                action="xp_awarded",
                resource_type="user",
                resource_id=user_id,
                details={
                    "xp_amount": xp_amount,
                    "reason": reason,
                    "old_xp": old_xp,
                    "new_xp": user.xp,
                    "old_level": old_level,
                    "new_level": user.level,
                    "badges_earned": [badge["id"] for badge in earned_badges]
                },
                success="success",
                db=db
            )
            
            logger.info(f"XP awarded: {xp_amount} to user {user_id} for {reason}. New total: {user.xp}, Level: {user.level}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error awarding XP: {str(e)}")
            return False
    
    @staticmethod
    def check_badge_earnings(user: User, old_xp: int, new_xp: int, db: Session) -> list:
        earned_badges = []
        
        # Check for various badge conditions
        earned_badges.extend(XPService._check_first_post_badge(user, db))
        earned_badges.extend(XPService._check_course_completion_badges(user, old_xp, new_xp, db))
        earned_badges.extend(XPService._check_task_completion_badges(user, old_xp, new_xp, db))
        earned_badges.extend(XPService._check_social_badges(user, old_xp, new_xp, db))
        earned_badges.extend(XPService._check_streak_badges(user, db))
        earned_badges.extend(XPService._check_quiz_badges(user, old_xp, new_xp, db))
        earned_badges.extend(XPService._check_level_badges(user, old_xp, new_xp))
        
        return earned_badges
    
    @staticmethod
    def _check_first_post_badge(user: User, db: Session) -> Optional[dict]:
        # MVP-SIMPLIFIED: Check if user has created posts
        from models.post import Post
        post_count = db.query(Post).filter(Post.user_id == user.id).count()
        
        if post_count == 1 and "first_post" not in [b.get("id") for b in user.badges or []]:
            return [badge for badge in XPService.BADGES if badge["id"] == "first_post"]
        return None
    
    @staticmethod
    def _check_course_completion_badges(user: User, old_xp: int, new_xp: int, db: Session) -> list:
        earned_badges = []
        
        # Check for course completion milestones
        if old_xp < 50 <= new_xp and "course_complete" not in [b.get("id") for b in user.badges or []]:
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "course_complete"])
        
        if old_xp < 200 <= new_xp and "course_complete" in [b.get("id") for b in user.badges or []]:
            # Second course completion
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "course_complete"])
        
        return earned_badges
    
    @staticmethod
    def _check_task_completion_badges(user: User, old_xp: int, new_xp: int, db: Session) -> list:
        earned_badges = []
        
        # Check for task completion milestones
        task_count = db.query(Submission).filter(
            Submission.user_id == user.id,
            Submission.status == "approved"
        ).count()
        
        if old_xp < 15 <= new_xp and "task_complete" not in [b.get("id") for b in user.badges or []]:
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "task_complete"])
        
        if old_xp < 150 <= new_xp and "task_complete" in [b.get("id") for b in user.badges or []]:
            # Task champion
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "task_champion"])
        
        return earned_badges
    
    @staticmethod
    def _check_social_badges(user: User, old_xp: int, new_xp: int, db: Session) -> list:
        earned_badges = []
        
        # Check for likes received
        from models.post import Post
        total_likes = db.query(Post).filter(Post.user_id == user.id).with_entities(Post.likes_count).all()
        likes_received = sum(post.likes_count for post in total_likes)
        
        if likes_received >= 10 and "social_butterfly" not in [b.get("id") for b in user.badges or []]:
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "social_butterfly"])
        
        return earned_badges
    
    @staticmethod
    def _check_streak_badges(user: User, db: Session) -> list:
        earned_badges = []
        
        # MVP-SIMPLIFIED: Check for login streak (would need login history)
        # For now, award based on activity
        if user.xp >= 500 and "streak_warrior" not in [b.get("id") for b in user.badges or []]:
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "streak_warrior"])
        
        return earned_badges
    
    @staticmethod
    def _check_quiz_badges(user: User, old_xp: int, new_xp: int, db: Session) -> list:
        earned_badges = []
        
        # Count perfect quiz scores
        from models.progress import Progress
        perfect_quizzes = db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.quiz_score == 100
        ).count()
        
        if perfect_quizzes >= 5 and "quiz_master" not in [b.get("id") for b in user.badges or []]:
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "quiz_master"])
        
        return earned_badges
    
    @staticmethod
    def _check_level_badges(user: User, old_xp: int, new_xp: int) -> list:
        earned_badges = []
        
        # Check for level milestones
        if new_xp >= 40000 and "level_10" not in [b.get("id") for b in user.badges or []]:
            earned_badges.append([badge for badge in XPService.BADGES if badge["id"] == "level_10"])
        
        return earned_badges
    
    @staticmethod
    def get_user_stats(user_id: int, db: Session) -> Optional[dict]:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Calculate stats
            from models.post import Post
            from models.submission import Submission
            from models.progress import Progress
            
            total_posts = db.query(Post).filter(Post.user_id == user_id).count()
            completed_tasks = db.query(Submission).filter(
                Submission.user_id == user_id,
                Submission.status == "approved"
            ).count()
            
            completed_modules = db.query(Progress).filter(
                Progress.user_id == user_id,
                Progress.completed == 1
            ).count()
            
            total_likes = db.query(Post).filter(Post.user_id == user_id).with_entities(Post.likes_count).all()
            likes_received = sum(post.likes_count for post in total_likes)
            
            return {
                "total_posts": total_posts,
                "completed_tasks": completed_tasks,
                "completed_modules": completed_modules,
                "total_likes": likes_received,
                "current_level": user.level,
                "xp_to_next_level": XPService.calculate_level(user.xp + 1)["min_xp"] - user.xp
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return None
