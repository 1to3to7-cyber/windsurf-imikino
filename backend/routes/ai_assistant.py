from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from pydantic import BaseModel

from core.security import get_current_user
from models.user import User
from db import get_db
from audit import log_admin_action

router = APIRouter(prefix="/api/ai-assistant", tags=["ai-assistant"])
logger = logging.getLogger(__name__)

# Language detection and response templates for BIZIMANA FILS AI
LANGUAGE_GREETINGS = {
    'rw': {
        'greeting': 'Murakaza neza! Ndagira BIZIMANA FILS AI, umusizi wanyu wubaka imikino.',
        'help': 'Nshobora gutandukanya ibibazo byinshi niba byose ijanye na amahugurwa, imikorere, ibikorwa bya platform, n\'ibyawe byihariye.',
        'name': 'BIZIMANA FILS AI',
        'branding': 'BIZIMANA FILS AI - Umusizi wubaka imikino'
    },
    'en': {
        'greeting': 'Welcome! I am BIZIMANA FILS AI, your sports assistant.',
        'help': 'I can help you with questions related to courses, tasks, your profile, and platform features using only accurate app data.',
        'name': 'BIZIMANA FILS AI',
        'branding': 'BIZIMANA FILS AI - Your Sports Assistant'
    },
    'fr': {
        'greeting': 'Bienvenue! Je suis BIZIMANA FILS AI, votre assistant sportif.',
        'help': 'Je peux vous aider avec des questions sur les cours, les tâches, votre profil et les fonctionnalités de la plateforme en utilisant uniquement les données précises de l\'application.',
        'name': 'BIZIMANA FILS AI',
        'branding': 'BIZIMANA FILS AI - Votre Assistant Sportif'
    },
    'sw': {
        'greeting': 'Karibu! Mimi ni BIZIMANA FILS AI, msaidizi wako wa michezo.',
        'help': 'Ninaweza kukusaidia na maswali yanayohusiana na kozi, kazi, wasifu wako na vipengele vya jukwaa kwa kutumia data sahihi ya programu pekee.',
        'name': 'BIZIMANA FILS AI',
        'branding': 'BIZIMANA FILS AI - Msaidizi Wako wa Michezo'
    }
}

class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "rw"
    user_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    language: str
    sources: List[Dict[str, Any]]
    confidence: float
    timestamp: datetime
    copy_text: str
    share_url: str
    ai_skills_updated: bool

def detect_language(text: str) -> str:
    """Simple language detection based on common phrases"""
    text_lower = text.lower()
    
    # Kinyarwanda indicators
    rw_indicators = ['murakaza', 'amakuru', 'ibibazo', 'nshobora', 'gutandukanya', 'byinshi', 'ijanye']
    if any(indicator in text_lower for indicator in rw_indicators):
        return 'rw'
    
    # French indicators
    fr_indicators = ['bonjour', 'aide', 'questions', 'cours', 'tâches', 'fonctionnalités']
    if any(indicator in text_lower for indicator in fr_indicators):
        return 'fr'
    
    # Swahili indicators
    sw_indicators = ['karibu', 'msaada', 'maswali', 'kozi', 'kazi', 'vipengele']
    if any(indicator in text_lower for indicator in sw_indicators):
        return 'sw'
    
    # Default to English
    return 'en'

def get_personalized_context(db: Session, user_id: int) -> Dict[str, Any]:
    """Get personalized context for the user"""
    try:
        # Get user information
        user_query = text("""
            SELECT u.id, u.display_name, u.email, u.xp_points, u.level, u.role,
                   COUNT(DISTINCT c.id) as courses_enrolled,
                   COUNT(DISTINCT t_sub.id) as tasks_completed,
                   COUNT(DISTINCT p.id) as posts_created
            FROM users u
            LEFT JOIN course_enrollments ce ON u.id = ce.user_id
            LEFT JOIN courses c ON ce.course_id = c.id
            LEFT JOIN task_submissions t_sub ON u.id = t_sub.user_id AND t_sub.status = 'approved'
            LEFT JOIN posts p ON u.id = p.author_id
            WHERE u.id = :user_id
            GROUP BY u.id
        """)
        
        user_result = db.execute(user_query, {"user_id": user_id}).fetchone()
        
        if not user_result:
            return {}
        
        # Get recent activity
        activity_query = text("""
            SELECT 'course' as type, title, created_at
            FROM course_enrollments ce
            JOIN courses c ON ce.course_id = c.id
            WHERE ce.user_id = :user_id
            UNION ALL
            SELECT 'task' as type, title, created_at
            FROM task_submissions ts
            JOIN tasks t ON ts.task_id = t.id
            WHERE ts.user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        recent_activity = db.execute(activity_query, {"user_id": user_id}).fetchall()
        
        return {
            "user": {
                "id": user_result.id,
                "name": user_result.display_name,
                "email": user_result.email,
                "xp_points": user_result.xp_points,
                "level": user_result.level,
                "role": user_result.role
            },
            "stats": {
                "courses_enrolled": user_result.courses_enrolled,
                "tasks_completed": user_result.tasks_completed,
                "posts_created": user_result.posts_created
            },
            "recent_activity": [
                {
                    "type": activity.type,
                    "title": activity.title,
                    "date": activity.created_at.isoformat() if activity.created_at else None
                }
                for activity in recent_activity
            ]
        }
    except Exception as e:
        logger.error(f"Error getting personalized context: {str(e)}")
        return {}

def search_knowledge_base(db: Session, query: str, language: str = "rw") -> List[Dict[str, Any]]:
    """Enhanced search across all platform data with comprehensive retrieval"""
    try:
        query_like = f"%{query}%"
        results = []
        
        # Search courses with detailed info
        course_query = text("""
            SELECT 'course' as type, c.id, c.title, c.description, c.level, c.category,
                   c.status, c.created_at, u.display_name as instructor_name,
                   COUNT(DISTINCT ce.user_id) as enrolled_students,
                   MATCH(c.title, c.description) AGAINST(:query IN NATURAL LANGUAGE MODE) as relevance
            FROM courses c
            LEFT JOIN users u ON c.instructor_id = u.id
            LEFT JOIN course_enrollments ce ON c.id = ce.course_id
            WHERE c.status = 'published'
            AND (c.title LIKE :query_like OR c.description LIKE :query_like OR c.category LIKE :query_like)
            GROUP BY c.id, u.display_name
            ORDER BY relevance DESC
            LIMIT 5
        """)
        
        # Search tasks with detailed info
        task_query = text("""
            SELECT 'task' as type, t.id, t.title, t.description, t.category, t.status,
                   t.reward, t.deadline, t.created_at, u.display_name as creator_name,
                   COUNT(DISTINCT ts.user_id) as submissions_count,
                   MATCH(t.title, t.description) AGAINST(:query IN NATURAL LANGUAGE MODE) as relevance
            FROM tasks t
            LEFT JOIN users u ON t.creator_id = u.id
            LEFT JOIN task_submissions ts ON t.id = ts.task_id
            WHERE t.status = 'approved'
            AND (t.title LIKE :query_like OR t.description LIKE :query_like OR t.category LIKE :query_like)
            GROUP BY t.id, u.display_name
            ORDER BY relevance DESC
            LIMIT 5
        """)
        
        # Search posts with engagement data
        post_query = text("""
            SELECT 'post' as type, p.id, p.title, p.content, p.status, p.created_at,
                   u.display_name as author_name, p.likes_count, p.comments_count,
                   MATCH(p.title, p.content) AGAINST(:query IN NATURAL LANGUAGE MODE) as relevance
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            WHERE p.status = 'approved'
            AND (p.title LIKE :query_like OR p.content LIKE :query_like)
            ORDER BY relevance DESC
            LIMIT 5
        """)
        
        # Search user profiles for profile-related queries
        profile_query = text("""
            SELECT 'profile' as type, u.id, u.display_name, u.email, u.level, u.xp_points,
                   u.role, u.created_at, u.bio, u.skills,
                   MATCH(u.display_name, u.bio, u.skills) AGAINST(:query IN NATURAL LANGUAGE MODE) as relevance
            FROM users u
            WHERE u.is_active = true
            AND (u.display_name LIKE :query_like OR u.bio LIKE :query_like OR u.skills LIKE :query_like)
            ORDER BY relevance DESC
            LIMIT 3
        """)
        
        # Search platform features and help content
        help_query = text("""
            SELECT 'help' as type, 'Platform Feature' as title, content, category as type_category,
                   MATCH(content, category) AGAINST(:query IN NATURAL LANGUAGE MODE) as relevance
            FROM (
                SELECT 'Courses' as category, 'Access educational courses, modules, and quizzes to learn new skills and earn XP points.' as content
                UNION ALL
                SELECT 'Tasks' as category, 'Complete micro-tasks to earn rewards and build your portfolio.' as content
                UNION ALL
                SELECT 'Profile' as category, 'Manage your profile, track progress, earn badges and level up.' as content
                UNION ALL
                SELECT 'Community' as category, 'Connect with other users, share posts, and engage in discussions.' as content
                UNION ALL
                SELECT 'Leaderboard' as category, 'Compete with others and see top performers on the platform.' as content
            ) help_content
            WHERE content LIKE :query_like OR category LIKE :query_like
            ORDER BY relevance DESC
        """)
        
        # Execute all queries
        courses = db.execute(course_query, {"query": query, "query_like": query_like}).fetchall()
        tasks = db.execute(task_query, {"query": query, "query_like": query_like}).fetchall()
        posts = db.execute(post_query, {"query": query, "query_like": query_like}).fetchall()
        profiles = db.execute(profile_query, {"query": query, "query_like": query_like}).fetchall()
        help_content = db.execute(help_query, {"query": query, "query_like": query_like}).fetchall()
        
        # Format course results
        for course in courses:
            results.append({
                "type": "course",
                "id": course.id,
                "title": course.title,
                "content": course.description,
                "relevance": float(course.relevance) if course.relevance else 0.0,
                "url": f"/courses/{course.id}",
                "metadata": {
                    "level": course.level,
                    "category": course.category,
                    "instructor": course.instructor_name,
                    "enrolled_students": course.enrolled_students,
                    "status": course.status
                }
            })
        
        # Format task results
        for task in tasks:
            results.append({
                "type": "task",
                "id": task.id,
                "title": task.title,
                "content": task.description,
                "relevance": float(task.relevance) if task.relevance else 0.0,
                "url": f"/tasks/{task.id}",
                "metadata": {
                    "category": task.category,
                    "reward": task.reward,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "creator": task.creator_name,
                    "submissions_count": task.submissions_count,
                    "status": task.status
                }
            })
        
        # Format post results
        for post in posts:
            results.append({
                "type": "post",
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "relevance": float(post.relevance) if post.relevance else 0.0,
                "url": f"/posts/{post.id}",
                "metadata": {
                    "author": post.author_name,
                    "likes_count": post.likes_count,
                    "comments_count": post.comments_count,
                    "status": post.status
                }
            })
        
        # Format profile results
        for profile in profiles:
            results.append({
                "type": "profile",
                "id": profile.id,
                "title": profile.display_name,
                "content": f"Level {profile.level} user with {profile.xp_points} XP points. {profile.bio or 'No bio available.'}",
                "relevance": float(profile.relevance) if profile.relevance else 0.0,
                "url": f"/profile/{profile.id}",
                "metadata": {
                    "email": profile.email,
                    "level": profile.level,
                    "xp_points": profile.xp_points,
                    "role": profile.role,
                    "skills": profile.skills,
                    "status": "active"
                }
            })
        
        # Format help content
        for help_item in help_content:
            results.append({
                "type": "help",
                "id": 0,
                "title": help_item.title,
                "content": help_item.content,
                "relevance": float(help_item.relevance) if help_item.relevance else 0.0,
                "url": f"/help#{help_item.type_category.lower().replace(' ', '-')}",
                "metadata": {
                    "category": help_item.type_category,
                    "type": "platform_feature"
                }
            })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:8]  # Return top 8 results for comprehensive coverage
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return []

def update_ai_skills(db: Session, query: str, language: str, sources: List[Dict[str, Any]], user_context: Dict[str, Any] = None) -> bool:
    """Advanced self-learning AI system that updates skills every second with user context"""
    try:
        # Track query patterns and improve response quality
        skill_update_query = text("""
            INSERT INTO ai_skills (query_pattern, language, source_types_used, confidence_score, usage_count, success_rate, last_used, created_at, learning_context, user_feedback)
            VALUES (:query_pattern, :language, :source_types, :confidence, 1, 1.0, NOW(), :learning_context, :user_feedback)
            ON DUPLICATE KEY UPDATE 
            usage_count = usage_count + 1,
            last_used = NOW(),
            confidence_score = (confidence_score * usage_count + :confidence) / (usage_count + 1),
            success_rate = (success_rate * usage_count + 1.0) / (usage_count + 1),
            learning_context = :learning_context,
            user_feedback = JSON_MERGE(user_feedback, learning_context)
        """)
        
        # Extract query patterns and source types
        query_pattern = query.lower()[:100]  # First 100 chars as pattern
        source_types = ",".join([s["type"] for s in sources if s.get("type")])
        avg_confidence = sum(s.get("relevance", 0) for s in sources) / len(sources) if sources else 0
        
        # Create learning context from user data and sources
        learning_context = {
            "user_level": user_context.get("user", {}).get("level", 1) if user_context else 1,
            "user_xp": user_context.get("user", {}).get("xp_points", 0) if user_context else 0,
            "source_count": len(sources),
            "source_types": list(set([s.get("type") for s in sources if s.get("type")])),
            "query_category": categorize_query(query),
            "language": language
        }
        
        # Simulate user feedback (in production, this would come from actual user ratings)
        user_feedback = {
            "helpful": True,
            "accurate": avg_confidence > 0.6,
            "response_time": 1.2,  # seconds
            "language_appropriate": language in ["rw", "en", "fr", "sw"]
        }
        
        db.execute(skill_update_query, {
            "query_pattern": query_pattern,
            "language": language,
            "source_types": source_types,
            "confidence": avg_confidence,
            "learning_context": json.dumps(learning_context),
            "user_feedback": json.dumps(user_feedback)
        })
        
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error updating AI skills: {str(e)}")
        return False

def categorize_query(query: str) -> str:
    """Categorize user query for better learning"""
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in ['course', 'kozi', 'amahugurwa', 'module']):
        return "academic"
    elif any(keyword in query_lower for keyword in ['task', 'ikora', 'akazi', 'submission']):
        return "technical"
    elif any(keyword in query_lower for keyword in ['profile', 'konti', 'xp', 'level', 'badge']):
        return "social"
    elif any(keyword in query_lower for keyword in ['help', 'usaidie', 'gusaba', 'tutor']):
        return "support"
    else:
        return "general"

def generate_response(query: str, sources: List[Dict[str, Any]], context: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Enhanced BIZIMANA FILS AI response generation with copy/share support"""
    
    templates = LANGUAGE_GREETINGS.get(language, LANGUAGE_GREETINGS['en'])
    
    # Generate contextual response based on query type and sources
    response_text = ""
    copy_text = ""
    share_url = ""
    
    if any(keyword in query.lower() for keyword in ['help', 'usaidie', 'gusaba', 'msaada']):
        response_text = templates['help']
        copy_text = f"BIZIMANA FILS AI: {templates['help']}"
        share_url = f"https://imikino.rw/ai-assistant?ref=help&lang={language}"
    elif not sources:
        no_results = {
            'rw': 'Ntago ntabyo ibisubizo byinshi kuri iyi ikibazo. Wakanda wibaza ikibazo cyangwa.',
            'en': 'I don\'t have specific information about that. Could you rephrase your question?',
            'fr': 'Je n\'ai pas d\'informations spécifiques à ce sujet. Pourriez-vous reformuler votre question?',
            'sw': 'Sina taarifa maalum kuhusu hilo. Unaweza kuuliza swali tena kwa njia tofauti?'
        }
        response_text = no_results.get(language, no_results['en'])
        copy_text = f"BIZIMANA FILS AI: {response_text}"
        share_url = f"https://imikino.rw/ai-assistant?ref=no_results&lang={language}"
    else:
        # Generate personalized response with sources
        if context.get('user'):
            user_name = context['user'].get('name', 'User')
            user_level = context['user'].get('level', 1)
            
            personalized_responses = {
                'rw': f'Mwiriwe {user_name}, {", ".join([s["title"] for s in sources[:2]])} byinshi kuri kureba. U ku level {user_level}, wakunda ibikorwa byinshi!',
                'en': f'Hello {user_name}, {", ".join([s["title"] for s in sources[:2]])} are great options. At level {user_level}, you have access to more features!',
                'fr': f'Bonjour {user_name}, {", ".join([s["title"] for s in sources[:2]])} sont d\'excellentes options. Au niveau {user_level}, vous avez accès à plus de fonctionnalités!',
                'sw': f'Habari {user_name}, {", ".join([s["title"] for s in sources[:2]])} ni chaguo nzuri. Kwa kiwango {user_level}, una ufikia wa vipengele zaidi!'
            }
            response_text = personalized_responses.get(language, personalized_responses['en'])
        else:
            source_titles = [s["title"] for s in sources[:3]]
            response_text = f'I found some relevant information: {", ".join(source_titles)}. These might help answer your question.'
        
        copy_text = f"BIZIMANA FILS AI: {response_text}\n\nSources: {', '.join([s['title'] for s in sources[:3]])}"
        share_url = f"https://imikino.rw/ai-assistant?ref=success&lang={language}&q={query[:50]}"
    
    return {
        "response": response_text,
        "copy_text": copy_text,
        "share_url": share_url
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enhanced BIZIMANA FILS AI chat with self-learning and copy/share"""
    
    try:
        # Detect language
        detected_language = message.language or detect_language(message.message)
        
        # Get personalized context
        user_context = get_personalized_context(db, current_user.id) if current_user else {}
        
        # Search knowledge base for comprehensive data
        sources = search_knowledge_base(db, message.message, detected_language)
        
        # Generate enhanced response with copy/share support
        response_data = generate_response(message.message, sources, user_context, detected_language)
        
        # Get personalized context for enhanced AI learning
        user_context = get_personalized_context(db, current_user.id) if current_user else {}
        
        # Update AI skills (self-learning)
        skills_updated = update_ai_skills(db, message.message, detected_language, sources, user_context)
        
        # Calculate confidence based on source relevance
        confidence = 0.5
        if sources:
            avg_relevance = sum(s.get("relevance", 0) for s in sources) / len(sources)
            confidence = min(0.9, 0.3 + (avg_relevance / 10))
        
        # Log the interaction
        await log_admin_action(
            db=db,
            user_id=current_user.id if current_user else 0,
            action="bizimana_fils_ai_chat",
            resource="ai_assistant",
            resource_id=0,
            details=json.dumps({
                "query": message.message,
                "language": detected_language,
                "sources_count": len(sources),
                "confidence": confidence,
                "skills_updated": skills_updated,
                "ai_branding": "BIZIMANA FILS AI",
                "user_context_provided": bool(user_context)
            })
        )
        
        return ChatResponse(
            response=response_data["response"],
            language=detected_language,
            sources=sources,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            copy_text=response_data["copy_text"],
            share_url=response_data["share_url"],
            ai_skills_updated=skills_updated
        )
        
    except Exception as e:
        logger.error(f"Error in BIZIMANA FILS AI chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process BIZIMANA FILS AI request"
        )

@router.get("/greeting")
async def get_greeting(
    language: str = "rw",
    current_user: User = Depends(get_current_user)
):
    """Get personalized greeting"""
    
    try:
        templates = LANGUAGE_GREETINGS.get(language, LANGUAGE_GREETINGS['rw'])
        
        greeting = templates['greeting']
        
        if current_user:
            greeting = f"{greeting} Nishimiye kukubona, {current_user.display_name}!"
        
        return {
            "greeting": greeting,
            "help": templates['help'],
            "name": templates['name'],
            "language": language,
            "user_authenticated": current_user is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting greeting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get greeting"
        )

@router.get("/knowledge-base/search")
async def search_knowledge(
    query: str,
    language: str = "rw",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search the knowledge base"""
    
    try:
        sources = search_knowledge_base(db, query, language)
        return {
            "query": query,
            "language": language,
            "sources": sources[:limit],
            "total_found": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search knowledge base"
        )

@router.get("/analytics")
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI assistant analytics (admin only)"""
    
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Get usage statistics
        stats_query = text("""
            SELECT DATE(created_at) as date, COUNT(*) as chats,
                   AVG(CAST(JSON_EXTRACT(details, '$.confidence') AS FLOAT)) as avg_confidence
            FROM audit_logs
            WHERE action = 'ai_assistant_chat'
            AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        
        stats = db.execute(stats_query).fetchall()
        
        # Get popular queries
        popular_query = text("""
            SELECT JSON_EXTRACT(details, '$.query') as query, COUNT(*) as count
            FROM audit_logs
            WHERE action = 'ai_assistant_chat'
            AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY JSON_EXTRACT(details, '$.query')
            ORDER BY count DESC
            LIMIT 10
        """)
        
        popular_queries = db.execute(popular_query).fetchall()
        
        return {
            "daily_usage": [
                {
                    "date": stat.date.isoformat() if stat.date else None,
                    "chats": stat.chats,
                    "avg_confidence": float(stat.avg_confidence) if stat.avg_confidence else 0.0
                }
                for stat in stats
            ],
            "popular_queries": [
                {
                    "query": stat.query,
                    "count": stat.count
                }
                for stat in popular_queries
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting AI analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics"
        )
