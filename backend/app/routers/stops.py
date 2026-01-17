"""
Stops Router - Bus stop list endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stop

router = APIRouter()


@router.get("/stops")
async def get_stops(
    city: Optional[str] = Query(None, description="Filter by city prefix in stop_id"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of stops to return"),
    db: Session = Depends(get_db)
):
    """
    Get list of all bus stops
    
    Returns stops with valid coordinates, optionally filtered by city.
    """
    try:
        query = db.query(Stop).filter(
            Stop.stop_lat.isnot(None),
            Stop.stop_lon.isnot(None),
            Stop.stop_lat != 0,
            Stop.stop_lon != 0
        )
        
        # Filter by city if provided (stop_id prefix)
        if city:
            query = query.filter(Stop.stop_id.ilike(f"{city}%"))
        
        stops = query.order_by(Stop.stop_name).limit(limit).all()
        
        return {
            "count": len(stops),
            "stops": [
                {
                    "stop_id": stop.stop_id,
                    "stop_name": stop.stop_name,
                    "stop_code": stop.stop_code,
                    "stop_lat": float(stop.stop_lat) if stop.stop_lat else None,
                    "stop_lon": float(stop.stop_lon) if stop.stop_lon else None,
                    "zone_id": stop.zone_id
                }
                for stop in stops
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stops: {str(e)}")


@router.get("/stops/{stop_id}")
async def get_stop(stop_id: str, db: Session = Depends(get_db)):
    """
    Get details for a specific bus stop
    """
    try:
        stop = db.query(Stop).filter(Stop.stop_id == stop_id).first()
        
        if not stop:
            raise HTTPException(status_code=404, detail=f"Stop {stop_id} not found")
        
        return {
            "stop_id": stop.stop_id,
            "stop_name": stop.stop_name,
            "stop_code": stop.stop_code,
            "stop_desc": stop.stop_desc,
            "stop_lat": float(stop.stop_lat) if stop.stop_lat else None,
            "stop_lon": float(stop.stop_lon) if stop.stop_lon else None,
            "zone_id": stop.zone_id,
            "location_type": stop.location_type,
            "wheelchair_boarding": stop.wheelchair_boarding
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stop: {str(e)}")
