"""
GTFS Router - Endpoints for downloading and importing GTFS data
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.gtfs import GTFSService, CITY_URLS

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/gtfs/cities")
async def list_cities():
    """List available cities for GTFS download"""
    return {
        "cities": list(CITY_URLS.keys()),
        "total": len(CITY_URLS)
    }


@router.post("/gtfs/download")
async def download_gtfs(
    city: Optional[str] = Query(None, description="City name (optional, downloads all if not specified)"),
    db: Session = Depends(get_db)
):
    """
    Download GTFS ZIP files from motionbuscard.org.cy
    
    If city is specified, downloads only that city.
    If city is not specified, downloads all available cities.
    """
    try:
        service = GTFSService(db)
        results = await service.download_gtfs(city)
        
        successful = sum(1 for v in results.values() if v.get('success'))
        
        return {
            "status": "success",
            "downloaded": successful,
            "total": len(results),
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading GTFS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to download GTFS: {str(e)}")


@router.post("/gtfs/import")
async def import_gtfs(
    city: Optional[str] = Query(None, description="City name (optional, imports all if not specified)"),
    db: Session = Depends(get_db)
):
    """
    Import GTFS data from downloaded ZIP files into database
    
    If city is specified, imports only that city.
    If city is not specified, imports all available cities.
    """
    try:
        service = GTFSService(db)
        results = service.import_gtfs(city)
        
        successful = sum(1 for v in results.values() if v.get('success'))
        
        return {
            "status": "success",
            "imported": successful,
            "total": len(results),
            "results": results
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing GTFS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to import GTFS: {str(e)}")


@router.post("/gtfs/sync")
async def sync_gtfs(
    city: Optional[str] = Query(None, description="City name (optional, syncs all if not specified)"),
    db: Session = Depends(get_db)
):
    """
    Download and import GTFS data in one step
    
    This is a convenience endpoint that downloads and then imports GTFS data.
    """
    try:
        service = GTFSService(db)
        
        # Download
        download_results = await service.download_gtfs(city)
        downloaded = sum(1 for v in download_results.values() if v.get('success'))
        
        if downloaded == 0:
            raise HTTPException(status_code=500, detail="No GTFS files were downloaded")
        
        # Import
        import_results = service.import_gtfs(city)
        imported = sum(1 for v in import_results.values() if v.get('success'))
        
        return {
            "status": "success",
            "downloaded": downloaded,
            "imported": imported,
            "download_results": download_results,
            "import_results": import_results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing GTFS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to sync GTFS: {str(e)}")


@router.get("/gtfs/stats")
async def get_gtfs_stats(db: Session = Depends(get_db)):
    """Get current GTFS database statistics"""
    try:
        service = GTFSService(db)
        stats = service.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "has_data": stats.get('stops', 0) > 0
        }
    except Exception as e:
        logger.error(f"Error getting GTFS stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
