import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('imikino.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.initialize_data()

    def create_tables(self):
        # Create users table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            role TEXT DEFAULT 'user' NOT NULL,
            xp INTEGER DEFAULT 0 NOT NULL,
            level INTEGER DEFAULT 1 NOT NULL,
            badges TEXT DEFAULT '[]',
            last_login_at TEXT,
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            deleted_at TEXT
        )''')

        # Create posts table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            media_url TEXT,
            type TEXT DEFAULT 'text',
            likes_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')

        # Create comments table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')

        # Create courses table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            thumbnail_url TEXT,
            modules TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        # Create quizzes table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL,
            questions TEXT,
            correct_answers TEXT
        )''')

        # Create quiz_submissions table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS quiz_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            answers TEXT,
            score INTEGER,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )''')

        # Create tasks table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            xp_reward INTEGER NOT NULL,
            deadline TEXT,
            proof_type TEXT DEFAULT 'text',
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        # Create task_submissions table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS task_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            proof TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT,
            reviewer_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (reviewer_id) REFERENCES users (id)
        )''')

        # Create audit_log table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')

        # Create contact_submissions table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS contact_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        self.conn.commit()

    def initialize_data(self):
        cursor = self.conn.cursor()
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
        
        self.conn.commit()

    def get_connection(self):
        return self.conn

# Global database instance
db = Database()
