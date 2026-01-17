"""
News Router - Government news management endpoints (bilingual support)
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import aiofiles

from app.database import get_db
from app.models import GovernmentNews

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("/news")
async def get_news(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all government news, optionally filtered by active status"""
    try:
        query = db.query(GovernmentNews)
        
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                GovernmentNews.is_active == True,
                (GovernmentNews.expires_at == None) | (GovernmentNews.expires_at > now)
            )
        
        news_items = query.order_by(GovernmentNews.display_order, GovernmentNews.created_at.desc()).all()
        
        return {
            "count": len(news_items),
            "news": [
                {
                    "id": item.id,
                    "title_el": item.title_el,
                    "content_el": item.content_el,
                    "title_en": item.title_en,
                    "content_en": item.content_en,
                    "image_url": item.image_url,
                    "source": item.source,
                    "duration_seconds": item.duration_seconds,
                    "is_active": item.is_active,
                    "display_order": item.display_order,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "expires_at": item.expires_at.isoformat() if item.expires_at else None
                }
                for item in news_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")


@router.get("/news/{news_id}")
async def get_news_item(news_id: int, db: Session = Depends(get_db)):
    """Get a specific news item by ID"""
    item = db.query(GovernmentNews).filter(GovernmentNews.id == news_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"News item {news_id} not found")
    
    return {
        "id": item.id,
        "title_el": item.title_el,
        "content_el": item.content_el,
        "title_en": item.title_en,
        "content_en": item.content_en,
        "image_url": item.image_url,
        "source": item.source,
        "duration_seconds": item.duration_seconds,
        "is_active": item.is_active,
        "display_order": item.display_order,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "expires_at": item.expires_at.isoformat() if item.expires_at else None
    }


@router.post("/news")
async def create_news(
    title_el: str = Form(...),
    content_el: str = Form(...),
    title_en: Optional[str] = Form(None),
    content_en: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    duration_seconds: int = Form(12),
    image: Optional[UploadFile] = File(None),
    expires_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new government news item (bilingual)"""
    try:
        image_url = None
        
        # Handle image upload if provided
        if image and image.filename:
            file_ext = os.path.splitext(image.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            file_content = await image.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            image_url = f"/uploads/{unique_filename}"
        
        # Parse expires_at if provided
        expires_datetime = None
        if expires_at:
            try:
                expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid expires_at format. Use ISO 8601.")
        
        # Create news record
        news_item = GovernmentNews(
            title_el=title_el,
            content_el=content_el,
            title_en=title_en,
            content_en=content_en,
            source=source,
            duration_seconds=duration_seconds,
            image_url=image_url,
            expires_at=expires_datetime,
            is_active=True
        )
        
        db.add(news_item)
        db.commit()
        db.refresh(news_item)
        
        logger.info(f"Created news item {news_item.id}: {title_el}")
        
        return {
            "id": news_item.id,
            "title_el": news_item.title_el,
            "title_en": news_item.title_en,
            "message": "News item created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create news: {str(e)}")


@router.put("/news/{news_id}")
async def update_news(
    news_id: int,
    title_el: Optional[str] = Form(None),
    content_el: Optional[str] = Form(None),
    title_en: Optional[str] = Form(None),
    content_en: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    duration_seconds: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    is_active: Optional[bool] = Form(None),
    display_order: Optional[int] = Form(None),
    expires_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update an existing news item"""
    item = db.query(GovernmentNews).filter(GovernmentNews.id == news_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"News item {news_id} not found")
    
    try:
        # Update fields if provided
        if title_el is not None:
            item.title_el = title_el
        if content_el is not None:
            item.content_el = content_el
        if title_en is not None:
            item.title_en = title_en
        if content_en is not None:
            item.content_en = content_en
        if source is not None:
            item.source = source
        if duration_seconds is not None:
            item.duration_seconds = duration_seconds
        if is_active is not None:
            item.is_active = is_active
        if display_order is not None:
            item.display_order = display_order
        if expires_at is not None:
            if expires_at == "":
                item.expires_at = None
            else:
                item.expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        # Handle new image upload
        if image and image.filename:
            file_ext = os.path.splitext(image.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            file_content = await image.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Delete old image if it exists
            if item.image_url:
                old_path = os.path.join(UPLOAD_DIR, os.path.basename(item.image_url))
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            item.image_url = f"/uploads/{unique_filename}"
        
        db.commit()
        db.refresh(item)
        
        return {
            "id": item.id,
            "title_el": item.title_el,
            "title_en": item.title_en,
            "message": "News item updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating news {news_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update news: {str(e)}")


@router.delete("/news/{news_id}")
async def delete_news(news_id: int, db: Session = Depends(get_db)):
    """Delete a news item"""
    item = db.query(GovernmentNews).filter(GovernmentNews.id == news_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"News item {news_id} not found")
    
    try:
        # Delete image file if it exists
        if item.image_url:
            file_path = os.path.join(UPLOAD_DIR, os.path.basename(item.image_url))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.delete(item)
        db.commit()
        
        logger.info(f"Deleted news item {news_id}")
        
        return {"message": f"News item {news_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting news {news_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete news: {str(e)}")
