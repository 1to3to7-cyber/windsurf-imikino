from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import timedelta
from models import UserCreate, UserLogin, Token, UserResponse
from auth import authenticate_user, create_access_token, get_password_hash, get_user_by_email, ACCESS_TOKEN_EXPIRE_MINUTES
from db import db

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    password_hash = get_password_hash(user.password)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (email, password_hash, display_name, xp, role, badges)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user.email,
        password_hash,
        user.display_name,
        0,  # Starting XP
        "user",
        "[]"  # Empty badges array
    ))
    conn.commit()
    
    # Get created user
    user_id = cursor.lastrowid
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()
    
    user_response = UserResponse(
        id=user_row["id"],
        email=user_row["email"],
        display_name=user_row["display_name"],
        xp=user_row["xp"],
        role=user_row["role"],
        badges=eval(user_row["badges"]) if isinstance(user_row["badges"], str) else user_row["badges"],
        created_at=user_row["created_at"]
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token."""
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
