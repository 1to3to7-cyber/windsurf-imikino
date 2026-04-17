from fastapi import APIRouter, Depends, HTTPException, status
from models import CourseResponse, QuizResponse, QuizSubmission, UserProgress
from auth import get_current_user, award_xp, check_and_award_badge
from db import db
import json

router = APIRouter()

@router.get("/", response_model=list[CourseResponse])
async def get_courses(current_user: dict = Depends(get_current_user)):
    """Get all courses with user progress."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM courses ORDER BY created_at DESC")
    courses_rows = cursor.fetchall()
    
    courses_list = []
    for row in courses_rows:
        # Get user progress for this course
        cursor.execute('''
            SELECT COUNT(*) as completed_modules
            FROM progress
            WHERE user_id = ? AND course_id = ? AND completed = TRUE
        ''', (current_user.id, row["id"]))
        
        progress_row = cursor.fetchone()
        completed_modules = progress_row["completed_modules"] if progress_row else 0
        
        modules = json.loads(row["modules"]) if isinstance(row["modules"], str) else row["modules"]
        total_modules = len(modules)
        
        courses_list.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "thumbnail_url": row["thumbnail_url"],
            "modules": modules,
            "created_at": row["created_at"],
            "progress": {
                "completed_modules": completed_modules,
                "total_modules": total_modules,
                "completion_percentage": (completed_modules / total_modules * 100) if total_modules > 0 else 0
            }
        })
    
    conn.close()
    return courses_list

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific course with user progress."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course_row = cursor.fetchone()
    
    if not course_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get user progress for each module
    modules = json.loads(course_row["modules"]) if isinstance(course_row["modules"], str) else course_row["modules"]
    
    for module in modules:
        cursor.execute('''
            SELECT completed, quiz_score
            FROM progress
            WHERE user_id = ? AND course_id = ? AND module_id = ?
        ''', (current_user.id, course_id, module["id"]))
        
        progress_row = cursor.fetchone()
        if progress_row:
            module["completed"] = bool(progress_row["completed"])
            module["quiz_score"] = progress_row["quiz_score"]
        else:
            module["completed"] = False
            module["quiz_score"] = 0
    
    conn.close()
    
    return {
        "id": course_row["id"],
        "title": course_row["title"],
        "description": course_row["description"],
        "thumbnail_url": course_row["thumbnail_url"],
        "modules": modules,
        "created_at": course_row["created_at"]
    }

@router.get("/{course_id}/quizzes/{module_id}", response_model=QuizResponse)
async def get_module_quiz(course_id: int, module_id: str, current_user: dict = Depends(get_current_user)):
    """Get quiz for a specific module."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if course exists
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course_row = cursor.fetchone()
    
    if not course_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if module exists in course
    modules = json.loads(course_row["modules"]) if isinstance(course_row["modules"], str) else course_row["modules"]
    module_exists = any(module["id"] == module_id for module in modules)
    
    if not module_exists:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Get quiz
    cursor.execute("SELECT * FROM quizzes WHERE module_id = ?", (module_id,))
    quiz_row = cursor.fetchone()
    
    if not quiz_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found for this module"
        )
    
    questions = json.loads(quiz_row["questions"]) if isinstance(quiz_row["questions"], str) else quiz_row["questions"]
    
    conn.close()
    
    return {
        "id": quiz_row["id"],
        "module_id": quiz_row["module_id"],
        "questions": questions
    }

@router.post("/{course_id}/quizzes/{module_id}/submit")
async def submit_quiz(course_id: int, module_id: str, submission: QuizSubmission, current_user: dict = Depends(get_current_user)):
    """Submit quiz answers for a module."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get quiz and correct answers
    cursor.execute("SELECT * FROM quizzes WHERE module_id = ?", (module_id,))
    quiz_row = cursor.fetchone()
    
    if not quiz_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    correct_answers = json.loads(quiz_row["correct_answers"]) if isinstance(quiz_row["correct_answers"], str) else quiz_row["correct_answers"]
    
    # Calculate score
    score = 0
    for i, (user_answer, correct_answer) in enumerate(zip(submission.answers, correct_answers)):
        if user_answer == correct_answer:
            score += 1
    
    total_questions = len(correct_answers)
    score_percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Update or insert progress
    cursor.execute('''
        INSERT OR REPLACE INTO progress (user_id, course_id, module_id, completed, quiz_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_user.id, course_id, module_id, score_percentage >= 70, score))
    
    conn.commit()
    
    # Award XP based on performance
    xp_awarded = 0
    if score_percentage >= 70:
        xp_awarded = 50  # Base XP for passing
        if score_percentage == 100:
            xp_awarded = 75  # Bonus for perfect score
        
        award_xp(current_user.id, xp_awarded)
        
        # Check for course completion badge
        cursor.execute('''
            SELECT COUNT(*) as total_modules, 
                   SUM(CASE WHEN completed = TRUE THEN 1 ELSE 0 END) as completed_modules
            FROM progress
            WHERE user_id = ? AND course_id = ?
        ''', (current_user.id, course_id))
        
        progress_info = cursor.fetchone()
        if progress_info["total_modules"] == progress_info["completed_modules"]:
            check_and_award_badge(current_user.id, "course_complete")
    
    conn.close()
    
    return {
        "score": score,
        "total_questions": total_questions,
        "score_percentage": score_percentage,
        "passed": score_percentage >= 70,
        "xp_awarded": xp_awarded
    }

@router.post("/{course_id}/modules/{module_id}/complete")
async def complete_module(course_id: int, module_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a module as completed (without quiz)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if course and module exist
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course_row = cursor.fetchone()
    
    if not course_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    modules = json.loads(course_row["modules"]) if isinstance(course_row["modules"], str) else course_row["modules"]
    module_exists = any(module["id"] == module_id for module in modules)
    
    if not module_exists:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Update progress
    cursor.execute('''
        INSERT OR REPLACE INTO progress (user_id, course_id, module_id, completed, quiz_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_user.id, course_id, module_id, True, 0))
    
    conn.commit()
    
    # Award XP for completing module
    award_xp(current_user.id, 25)
    
    conn.close()
    
    return {"message": "Module completed successfully", "xp_awarded": 25}
