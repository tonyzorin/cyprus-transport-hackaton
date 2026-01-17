"""
Arrivals Service - Scrapes real-time bus arrival data from Motion website
Scrapes real-time arrival data from motionbuscard.org.cy
"""
import logging
from datetime import timedelta
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup

from app.utils.timezone import get_cyprus_now, parse_gtfs_time
from app.utils.text import normalize_route_name

logger = logging.getLogger(__name__)

# Motion website base URL
MOTION_BASE_URL = "https://motionbuscard.org.cy/routes/stop"


async def fetch_realtime_arrivals(stop_id: str) -> List[Dict]:
    """
    Fetch real-time bus arrivals from Motion website
    
    Args:
        stop_id: The bus stop ID
        
    Returns:
        List of arrival dictionaries with route_short_name, arrival_time, time_left
    """
    realtime_arrivals = []
    
    try:
        motion_url = f"{MOTION_BASE_URL}/{stop_id}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(motion_url)
            
            if response.status_code != 200:
                logger.debug(f"Motion website returned status {response.status_code} for stop {stop_id}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for item in soup.select('.arrivalTimes__list__item'):
                route_text = item.select_one('.line__item__text')
                arrival_text = item.select_one('.arrivalTimes__list__item__link__text2')
                
                if not route_text or not arrival_text:
                    continue
                
                # Extract route name (remove Greek "Διαδρομή" suffix if present)
                route_short_name = route_text.get_text(strip=True).split('Διαδρομή')[0].strip()
                arrival_time_text = arrival_text.get_text(strip=True)
                
                # Skip if no route name or placeholder text
                if not route_short_name or arrival_time_text == 'Προβλεπόενη ώρα σύμφων με το χρονοδιάγραμμα':
                    continue
                
                time_left = None
                arrival_time = None
                
                # Get current Cyprus time
                current_cyprus_time = get_cyprus_now()
                
                if 'Λεπτά' in arrival_time_text:
                    # Format: "5 Λεπτά" (5 Minutes)
                    try:
                        time_left = int(arrival_time_text.replace('Λεπτά', '').strip())
                        arrival_time = (current_cyprus_time + timedelta(minutes=time_left)).strftime('%H:%M:%S')
                    except ValueError:
                        continue
                else:
                    # Format: "19:30" (absolute time)
                    arrival_time = arrival_time_text
                    try:
                        # Parse as Cyprus local time
                        arrival_dt = parse_gtfs_time(arrival_time + ':00', current_cyprus_time)
                        
                        # If arrival time is before current time, it's for tomorrow
                        if arrival_dt < current_cyprus_time:
                            arrival_dt = parse_gtfs_time(arrival_time + ':00', current_cyprus_time + timedelta(days=1))
                        
                        time_left = int((arrival_dt - current_cyprus_time).total_seconds() / 60)
                    except Exception as e:
                        logger.debug(f"Error parsing arrival time {arrival_time}: {e}")
                        continue
                
                if time_left is not None and time_left >= 0:
                    realtime_arrivals.append({
                        'route_short_name': route_short_name,
                        'arrival_time': arrival_time,
                        'time_left': time_left,
                        'is_live': True
                    })
                    
    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching arrivals for stop {stop_id}")
    except Exception as e:
        logger.error(f"Error fetching arrivals for stop {stop_id}: {e}")
    
    return realtime_arrivals


def enrich_arrivals_with_route_info(
    arrivals: List[Dict],
    routes: List[Dict]
) -> List[Dict]:
    """
    Enrich arrival data with route information (colors, headsigns)
    
    Args:
        arrivals: List of arrival dictionaries from Motion
        routes: List of route dictionaries from database
        
    Returns:
        Enriched arrival list
    """
    enriched = []
    
    for arrival in arrivals:
        normalized_route = normalize_route_name(arrival['route_short_name'])
        
        # Find matching route info
        route_info = next(
            (r for r in routes if normalize_route_name(r.get('route_short_name', '')) == normalized_route),
            None
        )
        
        enriched.append({
            'route_short_name': arrival['route_short_name'],
            'arrival_time': arrival['arrival_time'],
            'time_left': arrival['time_left'],
            'route_id': route_info['route_id'] if route_info else None,
            'trip_headsign': route_info.get('trip_headsign', 'Unknown Destination') if route_info else 'Unknown Destination',
            'route_color': route_info.get('route_color', 'FFFFFF') if route_info else 'FFFFFF',
            'route_text_color': route_info.get('route_text_color', '000000') if route_info else '000000',
            'is_live': arrival.get('is_live', True)
        })
    
    # Sort by time_left
    enriched.sort(key=lambda x: x['time_left'])
    
    return enriched
