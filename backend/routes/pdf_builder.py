"""
PDF Builder API Route
Handles PDF generation with AI integration for Lovable and AI Studio compatibility
"""

import os
import io
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.dependencies import get_db
from services.email_service import send_email

router = APIRouter(prefix="/api/pdf", tags=["PDF Builder"])

class PDFRequest(BaseModel):
    """PDF generation request model"""
    title: str
    content: str
    template: Optional[str] = "default"
    style: Optional[str] = "professional"
    include_ai_prompt: Optional[bool] = True
    target_platform: Optional[str] = "lovable"  # lovable, aistudio, custom

class PDFSection(BaseModel):
    """PDF section model"""
    title: str
    content: str
    order: int = 0

class PDFBuildRequest(BaseModel):
    """Advanced PDF build request with AI integration"""
    title: str
    sections: List[PDFSection]
    metadata: Optional[Dict[str, Any]] = None
    ai_enhancement: Optional[bool] = True
    export_format: Optional[str] = "pdf"  # pdf, docx, html
    custom_prompt: Optional[str] = None

@router.post("/generate")
async def generate_pdf(request: PDFRequest, db: Session = Depends(get_db)):
    """Generate PDF with AI enhancement"""
    try:
        # AI-enhanced content processing
        enhanced_content = await enhance_content_with_ai(request.content, request.title)
        
        # Generate PDF with professional styling
        pdf_content = create_professional_pdf(
            title=request.title,
            content=enhanced_content,
            template=request.template,
            style=request.style
        )
        
        # Log PDF generation
        await log_pdf_generation(db, request.title, len(pdf_content))
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.title}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/build-advanced")
async def build_advanced_pdf(request: PDFBuildRequest, db: Session = Depends(get_db)):
    """Advanced PDF builder with AI Studio integration"""
    try:
        # Process sections with AI enhancement
        enhanced_sections = []
        for section in request.sections:
            enhanced_content = await enhance_content_with_ai(
                section.content, 
                section.title,
                custom_context=request.custom_prompt
            )
            enhanced_sections.append({
                "title": section.title,
                "content": enhanced_content,
                "order": section.order
            })
        
        # Generate comprehensive PDF
        pdf_content = create_comprehensive_pdf(
            title=request.title,
            sections=enhanced_sections,
            metadata=request.metadata,
            style=request.style
        )
        
        # Create export for different platforms
        if request.target_platform == "lovable":
            lovable_config = generate_lovable_config(request)
            return JSONResponse({
                "pdf_content": pdf_content.hex(),
                "lovable_config": lovable_config,
                "metadata": request.metadata
            })
        
        elif request.target_platform == "aistudio":
            aistudio_config = generate_aistudio_config(request)
            return JSONResponse({
                "pdf_content": pdf_content.hex(),
                "aistudio_config": aistudio_config,
                "metadata": request.metadata
            })
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.title}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced PDF build failed: {str(e)}")

@router.get("/templates")
async def get_pdf_templates():
    """Get available PDF templates"""
    templates = {
        "professional": {
            "name": "Professional Report",
            "description": "Clean, professional layout with headers",
            "preview": "/templates/professional.png"
        },
        "academic": {
            "name": "Academic Paper",
            "description": "Academic format with citations",
            "preview": "/templates/academic.png"
        },
        "creative": {
            "name": "Creative Portfolio",
            "description": "Creative layout with visual elements",
            "preview": "/templates/creative.png"
        },
        "minimal": {
            "name": "Minimal Design",
            "description": "Clean, minimal layout",
            "preview": "/templates/minimal.png"
        }
    }
    return JSONResponse(templates)

@router.post("/upload-and-convert")
async def upload_and_convert(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload file and convert to PDF with AI enhancement"""
    try:
        # Validate file
        if not file.filename.endswith(('.txt', '.md', '.docx', '.html')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Read file content
        content = await file.read()
        
        # AI enhancement
        enhanced_content = await enhance_content_with_ai(
            content.decode('utf-8'), 
            file.filename,
            enhancement_type="document_conversion"
        )
        
        # Generate PDF
        pdf_content = create_professional_pdf(
            title=file.filename.replace('.txt', '').replace('.md', '').replace('.docx', '').replace('.html', ''),
            content=enhanced_content,
            template="professional"
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={file.filename}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File conversion failed: {str(e)}")

@router.get("/history")
async def get_pdf_history(db: Session = Depends(get_db)):
    """Get PDF generation history"""
    try:
        # This would typically query a pdf_generations table
        history = [
            {
                "id": 1,
                "title": "Project Proposal",
                "created_at": "2026-04-17T10:30:00Z",
                "status": "completed",
                "file_size": "2.3 MB"
            },
            {
                "id": 2,
                "title": "Technical Documentation",
                "created_at": "2026-04-17T09:15:00Z",
                "status": "completed",
                "file_size": "1.8 MB"
            }
        ]
        return JSONResponse({"history": history})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PDF history: {str(e)}")

@router.delete("/delete/{pdf_id}")
async def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """Delete a generated PDF"""
    try:
        # Implementation would delete from database
        return JSONResponse({"message": "PDF deleted successfully"})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")

# AI Integration Functions
async def enhance_content_with_ai(content: str, title: str, custom_context: Optional[str] = None) -> str:
    """Enhance content using AI for better PDF generation"""
    # Simulate AI enhancement (in production, this would call real AI service)
    enhancement_prompt = f"""
    Enhance the following content for professional PDF generation:
    
    Title: {title}
    Content: {content[:500]}...
    
    {f'Custom Context: {custom_context}' if custom_context else ''}
    
    Please:
    1. Improve clarity and professionalism
    2. Add proper structure and formatting
    3. Enhance readability
    4. Maintain original meaning
    5. Add professional tone
    
    Return the enhanced content only.
    """
    
    # In production, this would call the actual AI service
    # For now, return enhanced version with basic improvements
    enhanced = f"""
    {title.upper()}
    
    {'=' * 50}
    
    {content}
    
    {'=' * 50}
    
    Generated with AI Enhancement
    Imikino Platform - Professional PDF Builder
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return enhanced

def create_professional_pdf(title: str, content: str, template: str = "default", style: str = "professional") -> bytes:
    """Create professional PDF with styling"""
    # This would use a PDF library like ReportLab or WeasyPrint
    # For now, return a placeholder PDF content
    
    pdf_header = f"""
    %PDF-1.7
    1 0 obj
    << /Title ({title})
    << /Creator (Imikino PDF Builder)
    << /Producer (BIZIMANA Fils)
    << /CreationDate (D:{datetime.now().strftime('%Y%m%d%H%M%S')})
    """
    
    pdf_content = f"""
    {pdf_header}
    2 0 obj
    << /Font (Helvetica)
    << /FontSize 12
    """
    
    # Add content pages
    lines = content.split('\n')
    y_position = 750
    
    for line in lines:
        if line.strip():
            pdf_content += f"BT 0 0 -12 {y_position} Td\n"
            pdf_content += f"({line.strip()}) Tj\n"
            y_position -= 20
            
            if y_position < 100:
                pdf_content += "ET\n"
                y_position = 750
    
    pdf_content += "ET\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000015 00000 n\n0000000030 00000 n\n0000000040 00000 n\n0000000058 00000 n\n0000000109 00000 n\n0000000112 00000 n\ntrailer\n<< /Size 40\nstartxref\n%%EOF"
    
    return pdf_content.encode('latin-1')

def create_comprehensive_pdf(title: str, sections: List[Dict], metadata: Optional[Dict] = None, style: str = "professional") -> bytes:
    """Create comprehensive PDF with multiple sections"""
    # Enhanced PDF generation with sections
    pdf_content = f"""
    Comprehensive PDF: {title}
    Sections: {len(sections)}
    Style: {style}
    Metadata: {metadata}
    """
    
    # For now, return basic PDF structure
    return create_professional_pdf(title, pdf_content, template, style)

def generate_lovable_config(request: PDFBuildRequest) -> Dict[str, Any]:
    """Generate configuration for Lovable AI platform"""
    return {
        "platform": "lovable",
        "project_type": "react_app",
        "components": [
            {
                "type": "pdf_viewer",
                "props": {
                    "content": request.sections,
                    "title": request.title,
                    "style": request.style
                }
            }
        ],
        "styling": {
            "theme": "professional",
            "colors": ["#0ea5e9", "#1f2937", "#10b981"],
            "fonts": ["Inter", "Roboto"]
        },
        "ai_integration": {
            "enabled": request.ai_enhancement,
            "model": "gpt-4",
            "enhancement_type": "content_optimization"
        }
    }

def generate_aistudio_config(request: PDFBuildRequest) -> Dict[str, Any]:
    """Generate configuration for AI Studio"""
    return {
        "platform": "aistudio",
        "project_type": "ai_enhanced_app",
        "components": [
            {
                "type": "document_generator",
                "props": {
                    "sections": request.sections,
                    "metadata": request.metadata,
                    "export_format": request.export_format
                }
            }
        ],
        "workflow": {
            "ai_enhancement": request.ai_enhancement,
            "custom_prompts": request.custom_prompt,
            "iteration_support": True
        },
        "export_options": {
            "formats": ["pdf", "docx", "html"],
            "quality": "high",
            "optimization": True
        }
    }

async def log_pdf_generation(db: Session, title: str, file_size: int):
    """Log PDF generation for analytics"""
    # Implementation would log to database
    print(f"PDF Generated: {title}, Size: {file_size} bytes")
    pass
