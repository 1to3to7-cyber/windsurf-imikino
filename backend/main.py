from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os

from auth import get_current_user, get_current_admin_user
from routes import auth, users, posts, courses, tasks, admin, admin_auto_grant, ai_assistant
from routes.contact import router as contact_router
from routes.admin_chamber import router as admin_chamber_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Imikino Backend Starting Up...")
    yield
    # Shutdown
    print("🛑 Imikino Backend Shutting Down...")

app = FastAPI(
    title="Imikino API",
    description="Social-learning + micro-task platform for Rwandan youth",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(admin_auto_grant.router, prefix="/admin", tags=["Admin Auto-Grant"])
app.include_router(ai_assistant.router, prefix="/api", tags=["AI Assistant"])
app.include_router(contact_router, prefix="/api", tags=["Contact"])
app.include_router(admin_chamber_router, prefix="/api", tags=["Admin Chamber"])

@app.get("/")
async def root():
    return {"message": "Welcome to Imikino API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "imikino-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
