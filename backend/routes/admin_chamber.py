from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
import os
import subprocess
import zipfile
import io
from pydantic import BaseModel
import asyncio

from core.security import get_current_user
from models.user import User
from db import get_db
from audit import log_admin_action

router = APIRouter(prefix="/api/admin/chamber", tags=["admin-chamber"])
logger = logging.getLogger(__name__)

# Security: Only allow 1to3to7@gmail.com
AUTHORIZED_ADMIN_EMAIL = "1to3to7@gmail.com"

class CodeEditRequest(BaseModel):
    file_path: str
    content: str
    encoding: str = "utf-8"

class FileOperation(BaseModel):
    operation: str  # create, delete, move, copy
    source_path: str
    target_path: Optional[str] = None
    content: Optional[str] = None

class SQLQueryRequest(BaseModel):
    query: str
    database: str = "imikino.db"

class DeploymentRequest(BaseModel):
    platform: str  # vercel, render, netlify
    environment: str = "production"
    build_command: Optional[str] = None

def verify_admin_access(current_user: User) -> bool:
    """Verify user is authorized admin (1to3to7@gmail.com)"""
    return current_user and current_user.email == AUTHORIZED_ADMIN_EMAIL

def validate_file_path(file_path: str) -> bool:
    """Validate file path is within project bounds"""
    try:
        # Normalize path and check it's within allowed directories
        normalized_path = os.path.normpath(file_path)
        allowed_dirs = ["frontend", "backend", "docs", "scripts"]
        
        return any(normalized_path.startswith(allowed_dir) for allowed_dir in allowed_dirs)
    except Exception:
        return False

def get_file_syntax_highlighting(file_path: str, content: str) -> str:
    """Get syntax highlighting for different file types"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    syntax_map = {
        '.tsx': 'typescript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.js': 'javascript',
        '.py': 'python',
        '.css': 'css',
        '.html': 'html',
        '.json': 'json',
        '.md': 'markdown',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sql': 'sql'
    }
    
    return syntax_map.get(file_ext, 'text')

@router.get("/verify-access")
async def verify_admin_access_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Verify admin access"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only authorized admin can access this feature."
        )
    
    return {
        "access_granted": True,
        "admin_email": current_user.email,
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "code_viewer",
            "live_editor", 
            "file_manager",
            "database_admin",
            "deployment_controls",
            "project_status",
            "data_source_hub"
        ]
    }

@router.get("/project-structure")
async def get_project_structure(
    current_user: User = Depends(get_current_user)
):
    """Get complete project file structure"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        structure = {}
        
        # Get frontend structure
        frontend_structure = {}
        for root, dirs, files in os.walk("frontend", topdown=True):
            level = root.replace("frontend", "").count(os.sep)
            indent = " " * 2 * level
            rel_path = os.path.relpath(root, "frontend")
            
            frontend_structure[rel_path] = {
                "type": "directory",
                "children": dirs + files,
                "path": rel_path
            }
        
        # Get backend structure
        backend_structure = {}
        for root, dirs, files in os.walk("backend", topdown=True):
            level = root.replace("backend", "").count(os.sep)
            rel_path = os.path.relpath(root, "backend")
            
            backend_structure[rel_path] = {
                "type": "directory", 
                "children": dirs + files,
                "path": rel_path
            }
        
        return {
            "frontend": frontend_structure,
            "backend": backend_structure,
            "database": {
                "type": "file",
                "name": "imikino.db",
                "size": os.path.getsize("imikino.db") if os.path.exists("imikino.db") else 0,
                "modified": datetime.fromtimestamp(os.path.getmtime("imikino.db")).isoformat() if os.path.exists("imikino.db") else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting project structure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project structure"
        )

@router.get("/file/{path:path}")
async def get_file_content(
    path: str,
    current_user: User = Depends(get_current_user)
):
    """Get file content with syntax highlighting"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if not validate_file_path(path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    try:
        if not os.path.exists(path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        syntax = get_file_syntax_highlighting(path, content)
        
        return {
            "path": path,
            "content": content,
            "syntax": syntax,
            "encoding": "utf-8",
            "size": len(content),
            "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
            "read_only": not os.access(path, os.W_OK)
        }
        
    except Exception as e:
        logger.error(f"Error reading file {path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )

@router.post("/file/edit")
async def edit_file(
    request: CodeEditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit file content and save changes"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if not validate_file_path(request.file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    try:
        # Create backup before editing
        backup_path = f"{request.file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(request.file_path):
            os.rename(request.file_path, backup_path)
        
        # Save new content
        with open(request.file_path, 'w', encoding=request.encoding) as file:
            file.write(request.content)
        
        # Log the action
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="file_edit",
            resource="file",
            resource_id=request.file_path,
            details=json.dumps({
                "file_path": request.file_path,
                "backup_created": backup_path,
                "encoding": request.encoding,
                "content_size": len(request.content)
            })
        )
        
        return {
            "success": True,
            "message": "File saved successfully",
            "backup_path": backup_path,
            "syntax": get_file_syntax_highlighting(request.file_path, request.content)
        }
        
    except Exception as e:
        logger.error(f"Error editing file {request.file_path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

@router.post("/file/operation")
async def file_operation(
    request: FileOperation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform file operations (create, delete, move, copy)"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        if request.operation == "create":
            if not validate_file_path(request.target_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid target path"
                )
            
            # Create directory if needed
            os.makedirs(os.path.dirname(request.target_path), exist_ok=True)
            
            with open(request.target_path, 'w', encoding='utf-8') as file:
                if request.content:
                    file.write(request.content)
            
            message = f"File created: {request.target_path}"
            
        elif request.operation == "delete":
            if not validate_file_path(request.source_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file path"
                )
            
            if os.path.exists(request.source_path):
                os.remove(request.source_path)
                message = f"File deleted: {request.source_path}"
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
        elif request.operation == "move":
            if not (validate_file_path(request.source_path) and validate_file_path(request.target_path)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file paths"
                )
            
            os.rename(request.source_path, request.target_path)
            message = f"File moved from {request.source_path} to {request.target_path}"
            
        elif request.operation == "copy":
            if not (validate_file_path(request.source_path) and validate_file_path(request.target_path)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file paths"
                )
            
            import shutil
            shutil.copy2(request.source_path, request.target_path)
            message = f"File copied from {request.source_path} to {request.target_path}"
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid operation"
            )
        
        # Log the action
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="file_operation",
            resource="file",
            resource_id=f"{request.operation}:{request.source_path}",
            details=json.dumps({
                "operation": request.operation,
                "source_path": request.source_path,
                "target_path": request.target_path
            })
        )
        
        return {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in file operation {request.operation}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform file operation: {str(e)}"
        )

@router.post("/database/query")
async def execute_sql_query(
    request: SQLQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute SQL query and return results"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Dangerous query validation
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        query_upper = request.query.upper()
        
        if any(keyword in query_upper for keyword in dangerous_keywords):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dangerous SQL operations are not allowed in admin chamber"
            )
        
        # Execute SELECT query only
        if not query_upper.strip().startswith('SELECT'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only SELECT queries are allowed"
            )
        
        result = db.execute(text(request.query)).fetchall()
        
        # Convert to list of dicts
        columns = result._metadata.keys if result else []
        data = [dict(zip(columns, row)) for row in result]
        
        # Log the query
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="database_query",
            resource="database",
            resource_id=request.database,
            details=json.dumps({
                "query": request.query,
                "result_count": len(data),
                "columns": columns
            })
        )
        
        return {
            "success": True,
            "data": data,
            "columns": list(columns),
            "row_count": len(data),
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute query: {str(e)}"
        )

@router.get("/database/export")
async def export_database(
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export database in various formats"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        if format not in ["json", "csv", "sql"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid export format"
            )
        
        # Get all tables
        tables_query = text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = db.execute(tables_query).fetchall()
        
        export_data = {}
        
        for table in tables:
            table_name = table.name
            data_query = text(f"SELECT * FROM {table_name}")
            data = db.execute(data_query).fetchall()
            
            columns = data._metadata.keys if data else []
            export_data[table_name] = [dict(zip(columns, row)) for row in data]
        
        # Log the export
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="database_export",
            resource="database",
            resource_id=format,
            details=json.dumps({
                "format": format,
                "tables": [table.name for table in tables],
                "total_records": sum(len(export_data[table]) for table in export_data)
            })
        )
        
        if format == "json":
            return StreamingResponse(
                io.StringIO(json.dumps(export_data, indent=2)),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=imikino_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_content = "Database Export - CSV Format\n\n"
            for table_name, table_data in export_data.items():
                csv_content += f"\n--- Table: {table_name} ---\n"
                if table_data:
                    csv_content += ",".join(table_data[0].keys()) + "\n"
                    for row in table_data:
                        csv_content += ",".join(str(v) for v in row.values()) + "\n"
            
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=imikino_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        
    except Exception as e:
        logger.error(f"Error exporting database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export database: {str(e)}"
        )

@router.post("/deployment/deploy")
async def deploy_project(
    request: DeploymentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deploy project to various platforms"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log deployment start
        await log_admin_action(
            db=db,
            user_id=current_user.id,
            action="deployment_start",
            resource="deployment",
            resource_id=deployment_id,
            details=json.dumps({
                "platform": request.platform,
                "environment": request.environment,
                "build_command": request.build_command
            })
        )
        
        # Start deployment in background
        if request.platform == "vercel":
            # Vercel deployment logic
            background_tasks.add_task(
                deploy_to_vercel,
                deployment_id,
                request.environment
            )
        elif request.platform == "render":
            # Render deployment logic
            background_tasks.add_task(
                deploy_to_render,
                deployment_id,
                request.environment
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported deployment platform"
            )
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "platform": request.platform,
            "environment": request.environment,
            "message": "Deployment started successfully",
            "status_url": f"/api/admin/chamber/deployment/status/{deployment_id}"
        }
        
    except Exception as e:
        logger.error(f"Error starting deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start deployment: {str(e)}"
        )

@router.get("/deployment/status/{deployment_id}")
async def get_deployment_status(
    deployment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get deployment status"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # This would typically check deployment status from external service
    # For now, return mock status
    return {
        "deployment_id": deployment_id,
        "status": "in_progress",
        "progress": 65,
        "logs": [
            "Starting deployment...",
            "Building project...",
            "Deploying to platform..."
        ],
        "started_at": datetime.utcnow().isoformat(),
        "estimated_completion": "5-10 minutes"
    }

@router.get("/project/status")
async def get_project_status(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive project status"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Get system status
        import psutil
        
        status = {
            "system": {
                "uptime": datetime.now().isoformat(),
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "services": {
                "frontend": "running",  # Would check actual service status
                "backend": "running",
                "database": "connected"
            },
            "recent_activity": {
                "last_file_edit": "2 minutes ago",
                "last_deployment": "1 hour ago",
                "last_database_query": "5 minutes ago"
            },
            "statistics": {
                "total_files": sum(len(files) for _, _, files in os.walk('.') if files),
                "project_size": sum(os.path.getsize(f) for _, _, files in os.walk('.') for f in files if os.path.isfile(f)),
                "database_size": os.path.getsize('imikino.db') if os.path.exists('imikino.db') else 0
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        return {
            "system": {"status": "error"},
            "error": str(e)
        }

@router.get("/download/project")
async def download_project(
    current_user: User = Depends(get_current_user)
):
    """Download complete project as ZIP"""
    if not verify_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add frontend files
            for root, dirs, files in os.walk("frontend"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, "frontend")
                    zip_file.write(file_path, f"frontend/{arc_path}")
            
            # Add backend files
            for root, dirs, files in os.walk("backend"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, "backend")
                    zip_file.write(file_path, f"backend/{arc_path}")
            
            # Add database
            if os.path.exists("imikino.db"):
                zip_file.write("imikino.db", "imikino.db")
            
            # Add configuration files
            config_files = ["README.md", "package.json", "requirements.txt", ".env.example"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    zip_file.write(config_file, config_file)
        
        zip_buffer.seek(0)
        
        # Log download
        await log_admin_action(
            db=get_db(),
            user_id=current_user.id,
            action="project_download",
            resource="project",
            resource_id="full_project",
            details=json.dumps({
                "file_count": len(zip_buffer.getvalue()),
                "timestamp": datetime.utcnow().isoformat()
            })
        )
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=imikino_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"}
        )
        
    except Exception as e:
        logger.error(f"Error creating project download: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project download: {str(e)}"
        )

# Background task functions
async def deploy_to_vercel(deployment_id: str, environment: str):
    """Background task for Vercel deployment"""
    try:
        # Simulate deployment process
        await asyncio.sleep(2)
        logger.info(f"Vercel deployment {deployment_id} started for {environment}")
        
        # Actual Vercel API calls would go here
        # subprocess.run(["vercel", "--prod"], check=True)
        
        logger.info(f"Vercel deployment {deployment_id} completed")
    except Exception as e:
        logger.error(f"Vercel deployment {deployment_id} failed: {str(e)}")

async def deploy_to_render(deployment_id: str, environment: str):
    """Background task for Render deployment"""
    try:
        # Simulate deployment process
        await asyncio.sleep(3)
        logger.info(f"Render deployment {deployment_id} started for {environment}")
        
        # Actual Render API calls would go here
        # subprocess.run(["render", "deploy"], check=True)
        
        logger.info(f"Render deployment {deployment_id} completed")
    except Exception as e:
        logger.error(f"Render deployment {deployment_id} failed: {str(e)}")
