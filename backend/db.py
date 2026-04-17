import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        if not cursor.fetchone():
            # Create admin user
            cursor.execute('''
                INSERT INTO users (email, password_hash, display_name, role, xp, badges)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "admin@imikino.rw",
                "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e", # password: admin123
                "Admin Imikino",
                "admin",
                1000,
                json.dumps(["founder", "admin"])
            ))
        
        # Check if courses exist
        cursor.execute("SELECT * FROM courses")
        if not cursor.fetchone():
            # Sample course 1: Digital Literacy
            modules1 = [
                {
                    "id": "mod1_1",
                    "title": "Introduction to Computers",
                    "type": "text",
                    "content": "Computers are electronic devices that process data. They consist of hardware (physical parts) and software (programs)."
                },
                {
                    "id": "mod1_2", 
                    "title": "Internet Basics",
                    "type": "text",
                    "content": "The Internet is a global network of computers. It allows us to access information, communicate, and share resources worldwide."
                }
            ]
            
            cursor.execute('''
                INSERT INTO courses (title, description, thumbnail_url, modules)
                VALUES (?, ?, ?, ?)
            ''', (
                "Digital Literacy Basics",
                "Learn fundamental computer and internet skills for the digital age.",
                "https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=Digital+Literacy",
                json.dumps(modules1)
            ))
            
            # Sample course 2: Entrepreneurship
            modules2 = [
                {
                    "id": "mod2_1",
                    "title": "What is Entrepreneurship?",
                    "type": "text", 
                    "content": "Entrepreneurship is the process of starting and running a business. It involves identifying opportunities and taking risks to create value."
                },
                {
                    "id": "mod2_2",
                    "title": "Business Planning",
                    "type": "text",
                    "content": "A business plan is a document that outlines your business goals, strategies, and how you'll achieve them."
                }
            ]
            
            cursor.execute('''
                INSERT INTO courses (title, description, thumbnail_url, modules)
                VALUES (?, ?, ?, ?)
            ''', (
                "Youth Entrepreneurship",
                "Discover how to turn your ideas into successful businesses.",
                "https://via.placeholder.com/300x200/10B981/FFFFFF?text=Entrepreneurship",
                json.dumps(modules2)
            ))
            
            # Add quizzes for modules
            course_id = 1
            for module in modules1:
                cursor.execute('''
                    INSERT INTO quizzes (module_id, questions, correct_answers)
                    VALUES (?, ?, ?)
                ''', (
                    module["id"],
                    json.dumps([
                        {
                            "question": f"What is the main topic of {module['title']}?",
                            "options": ["Computers", "Internet", "Both", "None"],
                            "type": "multiple_choice"
                        }
                    ]),
                    json.dumps([2]) # Index of correct answer
                ))
        
        # Check if tasks exist
        cursor.execute("SELECT * FROM tasks")
        if not cursor.fetchone():
            # Sample tasks
            tasks = [
                {
                    "title": "Share Your Learning Goals",
                    "description": "Write a short post about what you want to learn on Imikino and why it matters to you.",
                    "xp_reward": 50,
                    "proof_type": "text"
                },
                {
                    "title": "Complete Your Profile",
                    "description": "Upload a profile picture and write a brief bio about yourself.",
                    "xp_reward": 30,
                    "proof_type": "image"
                },
                {
                    "title": "Help a Community Member",
                    "description": "Find a question in the community and provide a helpful answer or resource.",
                    "xp_reward": 75,
                    "proof_type": "link"
                }
            ]
            
            for task in tasks:
                cursor.execute('''
                    INSERT INTO tasks (title, description, xp_reward, proof_type)
                    VALUES (?, ?, ?, ?)
                ''', (
                    task["title"],
                    task["description"], 
                    task["xp_reward"],
                    task["proof_type"]
                ))
        
        conn.commit()
        conn.close()

# Global database instance
db = Database()
