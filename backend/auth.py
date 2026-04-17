from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import TokenData, UserResponse
from db import db
import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
        return token_data
    except JWTError:
        return None

def get_user_by_email(email: str) -> Optional[UserResponse]:
    """Get user by email from database."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()
    
    if user_row:
        return UserResponse(
            id=user_row["id"],
            email=user_row["email"],
            display_name=user_row["display_name"],
            xp=user_row["xp"],
            role=user_row["role"],
            badges=eval(user_row["badges"]) if isinstance(user_row["badges"], str) else user_row["badges"],
            created_at=user_row["created_at"]
        )
    return None

def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
    """Authenticate user with email and password."""
    user = get_user_by_email(email)
    if not user:
        return None
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not verify_password(password, row["password_hash"]):
        return None
    
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_admin_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated admin user."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def award_xp(user_id: int, xp_amount: int) -> bool:
    """Award XP to a user."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (xp_amount, user_id))
    conn.commit()
    conn.close()
    return True

def check_and_award_badge(user_id: int, badge_name: str) -> bool:
    """Check if user has badge, award if not."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT badges FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row:
        badges = eval(row["badges"]) if isinstance(row["badges"], str) else row["badges"]
        if badge_name not in badges:
            badges.append(badge_name)
            cursor.execute("UPDATE users SET badges = ? WHERE id = ?", (str(badges), user_id))
            conn.commit()
            conn.close()
            return True
    
    conn.close()
    return False
