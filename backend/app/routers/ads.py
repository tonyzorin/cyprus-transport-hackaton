"""
Ads Router - Advertisement management endpoints
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from PIL import Image
import aiofiles

from app.database import get_db
from app.models import Ad

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("/ads")
async def get_ads(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all ads, optionally filtered by active status"""
    try:
        query = db.query(Ad)
        
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                Ad.is_active == True,
                (Ad.expires_at == None) | (Ad.expires_at > now)
            )
        
        ads = query.order_by(Ad.display_order, Ad.created_at.desc()).all()
        
        return {
            "count": len(ads),
            "ads": [
                {
                    "id": ad.id,
                    "title": ad.title,
                    "image_url": ad.image_url,
                    "link_url": ad.link_url,
                    "advertiser_name": ad.advertiser_name,
                    "is_active": ad.is_active,
                    "display_order": ad.display_order,
                    "duration_seconds": ad.duration_seconds,
                    "created_at": ad.created_at.isoformat() if ad.created_at else None,
                    "expires_at": ad.expires_at.isoformat() if ad.expires_at else None
                }
                for ad in ads
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ads: {str(e)}")


@router.get("/ads/{ad_id}")
async def get_ad(ad_id: int, db: Session = Depends(get_db)):
    """Get a specific ad by ID"""
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    
    if not ad:
        raise HTTPException(status_code=404, detail=f"Ad {ad_id} not found")
    
    return {
        "id": ad.id,
        "title": ad.title,
        "image_url": ad.image_url,
        "link_url": ad.link_url,
        "advertiser_name": ad.advertiser_name,
        "is_active": ad.is_active,
        "display_order": ad.display_order,
        "duration_seconds": ad.duration_seconds,
        "created_at": ad.created_at.isoformat() if ad.created_at else None,
        "updated_at": ad.updated_at.isoformat() if ad.updated_at else None,
        "expires_at": ad.expires_at.isoformat() if ad.expires_at else None
    }


@router.post("/ads")
async def create_ad(
    title: str = Form(...),
    image: UploadFile = File(...),
    link_url: Optional[str] = Form(None),
    advertiser_name: Optional[str] = Form(None),
    duration_seconds: int = Form(10),
    expires_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new ad with image upload"""
    try:
        # Validate file extension
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await image.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Parse expires_at if provided
        expires_datetime = None
        if expires_at:
            try:
                expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid expires_at format. Use ISO 8601.")
        
        # Create ad record
        ad = Ad(
            title=title,
            image_url=f"/uploads/{unique_filename}",
            link_url=link_url,
            advertiser_name=advertiser_name,
            duration_seconds=duration_seconds,
            expires_at=expires_datetime,
            is_active=True
        )
        
        db.add(ad)
        db.commit()
        db.refresh(ad)
        
        logger.info(f"Created ad {ad.id}: {title}")
        
        return {
            "id": ad.id,
            "title": ad.title,
            "image_url": ad.image_url,
            "message": "Ad created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ad: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create ad: {str(e)}")


@router.put("/ads/{ad_id}")
async def update_ad(
    ad_id: int,
    title: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    link_url: Optional[str] = Form(None),
    advertiser_name: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    display_order: Optional[int] = Form(None),
    duration_seconds: Optional[int] = Form(None),
    expires_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update an existing ad"""
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    
    if not ad:
        raise HTTPException(status_code=404, detail=f"Ad {ad_id} not found")
    
    try:
        # Update fields if provided
        if title is not None:
            ad.title = title
        if link_url is not None:
            ad.link_url = link_url
        if advertiser_name is not None:
            ad.advertiser_name = advertiser_name
        if is_active is not None:
            ad.is_active = is_active
        if display_order is not None:
            ad.display_order = display_order
        if duration_seconds is not None:
            ad.duration_seconds = duration_seconds
        if expires_at is not None:
            if expires_at == "":
                ad.expires_at = None
            else:
                ad.expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        # Handle new image upload
        if image:
            file_ext = os.path.splitext(image.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            content = await image.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Delete old image if it exists
            if ad.image_url:
                old_path = os.path.join(UPLOAD_DIR, os.path.basename(ad.image_url))
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Save new image
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            ad.image_url = f"/uploads/{unique_filename}"
        
        db.commit()
        db.refresh(ad)
        
        return {
            "id": ad.id,
            "title": ad.title,
            "image_url": ad.image_url,
            "message": "Ad updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ad {ad_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update ad: {str(e)}")


@router.delete("/ads/{ad_id}")
async def delete_ad(ad_id: int, db: Session = Depends(get_db)):
    """Delete an ad"""
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    
    if not ad:
        raise HTTPException(status_code=404, detail=f"Ad {ad_id} not found")
    
    try:
        # Delete image file if it exists
        if ad.image_url:
            file_path = os.path.join(UPLOAD_DIR, os.path.basename(ad.image_url))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.delete(ad)
        db.commit()
        
        logger.info(f"Deleted ad {ad_id}")
        
        return {"message": f"Ad {ad_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting ad {ad_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete ad: {str(e)}")
