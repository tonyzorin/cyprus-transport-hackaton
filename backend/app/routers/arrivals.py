"""
Arrivals Router - Real-time bus arrival endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case as sql_case

from app.database import get_db
from app.models import Stop, Route, Trip, StopTime
from app.services.arrivals import fetch_realtime_arrivals, enrich_arrivals_with_route_info

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/arrivals/{stop_id}")
async def get_arrivals(stop_id: str, db: Session = Depends(get_db)):
    """
    Get real-time bus arrivals for a specific stop
    
    Fetches live data from Motion website and enriches with GTFS route info.
    For prototype: works even without GTFS data in database.
    """
    try:
        # Try to get stop info from database (optional for prototype)
        stop = db.query(Stop).filter(Stop.stop_id == stop_id).first()
        
        if stop:
            stop_info = {
                "stop_id": stop.stop_id,
                "stop_name": stop.stop_name,
                "stop_lat": float(stop.stop_lat) if stop.stop_lat else None,
                "stop_lon": float(stop.stop_lon) if stop.stop_lon else None
            }
            # Get routes serving this stop from database
            routes = get_routes_for_stop(stop_id, db)
        else:
            # For prototype: allow fetching arrivals without GTFS data
            stop_info = {
                "stop_id": stop_id,
                "stop_name": f"Stop {stop_id}",
                "stop_lat": None,
                "stop_lon": None
            }
            routes = []
        
        # Fetch real-time arrivals from Motion website
        realtime_arrivals = await fetch_realtime_arrivals(stop_id)
        
        # Enrich with route information (if available)
        enriched_arrivals = enrich_arrivals_with_route_info(realtime_arrivals, routes)
        
        return {
            "stop_info": stop_info,
            "arrivals": enriched_arrivals,
            "routes": routes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching arrivals for stop {stop_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch arrivals: {str(e)}")


def get_routes_for_stop(stop_id: str, db: Session) -> list:
    """
    Get all routes that serve a specific stop with their info
    """
    try:
        # Get routes for this stop with stop position (origin/destination/intermediate)
        stop_sequence_subq = db.query(
            StopTime.stop_id,
            Trip.route_id,
            Trip.trip_headsign,
            StopTime.stop_sequence,
            func.max(StopTime.stop_sequence).over(partition_by=Trip.trip_id).label('max_sequence'),
            func.min(StopTime.stop_sequence).over(partition_by=Trip.trip_id).label('min_sequence')
        ).join(
            Trip, StopTime.trip_id == Trip.trip_id
        ).filter(
            StopTime.stop_id == stop_id
        ).subquery()
        
        # Get route details
        route_directions = db.query(
            Route.route_id,
            Route.route_short_name,
            Route.route_long_name,
            Route.route_color,
            Route.route_text_color,
            Trip.trip_headsign,
            sql_case(
                (stop_sequence_subq.c.stop_sequence == stop_sequence_subq.c.min_sequence, 'origin'),
                (stop_sequence_subq.c.stop_sequence == stop_sequence_subq.c.max_sequence, 'destination'),
                else_='intermediate'
            ).label('stop_position')
        ).join(
            Trip, Route.route_id == Trip.route_id
        ).join(
            StopTime, Trip.trip_id == StopTime.trip_id
        ).join(
            stop_sequence_subq, Route.route_id == stop_sequence_subq.c.route_id
        ).filter(
            StopTime.stop_id == stop_id
        ).distinct().all()
        
        # Convert to list of dicts
        routes = []
        seen_routes = set()
        
        for row in route_directions:
            route_key = row.route_short_name
            if route_key not in seen_routes:
                seen_routes.add(route_key)
                routes.append({
                    'route_id': row.route_id,
                    'route_short_name': row.route_short_name,
                    'route_long_name': row.route_long_name,
                    'route_color': row.route_color or 'FFFFFF',
                    'route_text_color': row.route_text_color or '000000',
                    'trip_headsign': row.trip_headsign,
                    'stop_position': row.stop_position
                })
        
        return routes
        
    except Exception as e:
        logger.error(f"Error getting routes for stop {stop_id}: {e}")
        return []
