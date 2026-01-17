"""
Timezone utilities for Cyprus bus system
GTFS times are stored in local Cyprus timezone (Asia/Nicosia / Europe/Nicosia)
Cyprus timezone utilities for GTFS time handling
"""
from datetime import datetime, timedelta
from typing import Optional
import pytz

# Cyprus timezone (both names are valid)
CYPRUS_TZ = pytz.timezone('Asia/Nicosia')  # Same as Europe/Nicosia


def get_cyprus_now() -> datetime:
    """
    Get current time in Cyprus timezone
    
    Returns:
        datetime object with Cyprus timezone info
    """
    return datetime.now(CYPRUS_TZ)


def parse_gtfs_time(time_str: str, reference_date: Optional[datetime] = None) -> datetime:
    """
    Parse a GTFS time string (HH:MM:SS) as Cyprus local time
    
    GTFS times can exceed 24:00:00 to represent times on the next day.
    For example, 25:30:00 means 01:30:00 the next day.
    
    Args:
        time_str: Time string in HH:MM:SS format (can exceed 24:00:00)
        reference_date: Reference date (defaults to today in Cyprus timezone)
    
    Returns:
        datetime object in Cyprus timezone
    """
    if not time_str:
        raise ValueError("Time string cannot be empty")
    
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    seconds = int(parts[2]) if len(parts) > 2 else 0
    
    # Handle times >= 24:00:00 (next day)
    days_offset = 0
    if hours >= 24:
        days_offset = hours // 24
        hours = hours % 24
    
    if reference_date is None:
        reference_date = get_cyprus_now()
    else:
        # Ensure reference_date is in Cyprus timezone
        if reference_date.tzinfo is None:
            reference_date = CYPRUS_TZ.localize(reference_date)
        elif reference_date.tzinfo != CYPRUS_TZ:
            reference_date = reference_date.astimezone(CYPRUS_TZ)
    
    # Create time in Cyprus timezone
    result = reference_date.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
    
    # Add days if needed
    if days_offset > 0:
        result = result + timedelta(days=days_offset)
    
    return result


def format_gtfs_time(dt: datetime) -> str:
    """
    Format a datetime as GTFS time string (HH:MM:SS)
    
    Args:
        dt: datetime object (will be converted to Cyprus timezone if needed)
    
    Returns:
        Time string in HH:MM:SS format
    """
    if dt.tzinfo is None:
        dt = CYPRUS_TZ.localize(dt)
    elif dt.tzinfo != CYPRUS_TZ:
        dt = dt.astimezone(CYPRUS_TZ)
    
    return dt.strftime('%H:%M:%S')


def time_to_seconds_cyprus(time_str: str) -> int:
    """
    Convert GTFS time string to seconds since midnight (Cyprus time)
    
    Args:
        time_str: Time string in HH:MM:SS format
    
    Returns:
        Seconds since midnight
    """
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    seconds = int(parts[2]) if len(parts) > 2 else 0
    
    # Handle times >= 24:00:00
    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    return total_seconds


def seconds_to_time_cyprus(seconds: int) -> str:
    """
    Convert seconds since midnight to GTFS time string
    
    Args:
        seconds: Seconds since midnight (can exceed 86400 for next day)
    
    Returns:
        Time string in HH:MM:SS format
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
