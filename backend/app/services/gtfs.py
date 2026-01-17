"""
GTFS Service - Download and import GTFS data from motionbuscard.org.cy
"""
import os
import zipfile
import csv
import logging
import httpx
from pathlib import Path
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

# GTFS URLs for each city from motionbuscard.org.cy/opendata
CITY_URLS = {
    'limassol': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C6_google_transit.zip&rel=True",
    'pafos': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C2_google_transit.zip&rel=True",
    'famagusta': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C4_google_transit.zip&rel=True",
    'intercity': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C5_google_transit.zip&rel=True",
    'nicosia': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C9_google_transit.zip&rel=True",
    'larnaca': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C10_google_transit.zip&rel=True",
    'pame_express': "https://motionbuscard.org.cy/opendata/downloadfile?file=GTFS%5C11_google_transit.zip&rel=True"
}


class GTFSService:
    """Service for downloading and importing GTFS data"""
    
    def __init__(self, db: Session, gtfs_dir: str = '/app/gtfs_data'):
        self.db = db
        self.gtfs_dir = Path(gtfs_dir)
        self.gtfs_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_gtfs(self, city: Optional[str] = None) -> Dict[str, Any]:
        """
        Download GTFS files from motionbuscard.org.cy
        
        Args:
            city: Optional city name. If None, downloads all cities.
        
        Returns:
            Dictionary with download results
        """
        if city:
            if city not in CITY_URLS:
                raise ValueError(f"Unknown city: {city}. Available: {', '.join(CITY_URLS.keys())}")
            cities = {city: CITY_URLS[city]}
        else:
            cities = CITY_URLS
        
        results = {}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for city_name, url in cities.items():
                try:
                    logger.info(f"Downloading GTFS for {city_name}...")
                    response = await client.get(
                        url,
                        headers={
                            'Accept': '*/*',
                            'User-Agent': 'Bus-Hackaton/1.0'
                        },
                        follow_redirects=True
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"Failed to download {city_name}: HTTP {response.status_code}")
                        results[city_name] = {'success': False, 'error': f'HTTP {response.status_code}'}
                        continue
                    
                    zip_path = self.gtfs_dir / f"{city_name}.zip"
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = zip_path.stat().st_size
                    logger.info(f"Downloaded {city_name}: {file_size / 1024 / 1024:.2f} MB")
                    results[city_name] = {
                        'success': True,
                        'file': str(zip_path),
                        'size_mb': round(file_size / 1024 / 1024, 2)
                    }
                    
                except Exception as e:
                    logger.error(f"Error downloading {city_name}: {e}")
                    results[city_name] = {'success': False, 'error': str(e)}
        
        return results
    
    def import_gtfs(self, city: Optional[str] = None) -> Dict[str, Any]:
        """
        Import GTFS data from downloaded ZIP files into database
        
        Args:
            city: Optional city name. If None, imports all available cities.
        
        Returns:
            Dictionary with import results
        """
        if city:
            zip_path = self.gtfs_dir / f"{city}.zip"
            if not zip_path.exists():
                raise FileNotFoundError(f"GTFS file not found: {zip_path}")
            cities = [(city, zip_path)]
        else:
            cities = []
            for city_name in CITY_URLS.keys():
                zip_path = self.gtfs_dir / f"{city_name}.zip"
                if zip_path.exists():
                    cities.append((city_name, zip_path))
        
        results = {}
        
        for city_name, zip_path in cities:
            try:
                logger.info(f"Importing GTFS for {city_name}...")
                stats = self._import_gtfs_file(str(zip_path), city_name)
                results[city_name] = {'success': True, 'stats': stats}
            except Exception as e:
                logger.error(f"Error importing {city_name}: {e}")
                results[city_name] = {'success': False, 'error': str(e)}
        
        # Add indexes after import
        self._add_indexes()
        
        return results
    
    def _parse_csv_from_zip(self, zip_path: str, filename: str) -> List[Dict]:
        """Extract and parse a CSV file from a ZIP archive"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if filename not in zip_ref.namelist():
                    logger.debug(f"File {filename} not found in {zip_path}")
                    return []
                
                with zip_ref.open(filename) as f:
                    content = f.read()
                    if content.startswith(b'\xef\xbb\xbf'):
                        content = content[3:]
                    
                    text_content = content.decode('utf-8-sig')
                    reader = csv.DictReader(text_content.splitlines())
                    return list(reader)
        except Exception as e:
            logger.error(f"Error parsing {filename} from {zip_path}: {e}")
            return []
    
    def _import_gtfs_file(self, zip_path: str, city: str) -> Dict[str, int]:
        """Import a single GTFS ZIP file"""
        stats = {}
        
        # Import agency
        rows = self._parse_csv_from_zip(zip_path, 'agency.txt')
        for row in rows:
            self.db.execute(text("""
                INSERT INTO agency (agency_id, agency_name, agency_url, agency_timezone, agency_lang)
                VALUES (:agency_id, :agency_name, :agency_url, :agency_timezone, :agency_lang)
                ON CONFLICT (agency_id) DO NOTHING
            """), {
                'agency_id': row.get('agency_id', ''),
                'agency_name': row.get('agency_name', ''),
                'agency_url': row.get('agency_url', ''),
                'agency_timezone': row.get('agency_timezone', 'Europe/Nicosia'),
                'agency_lang': row.get('agency_lang', 'el')
            })
        stats['agency'] = len(rows)
        self.db.commit()
        
        # Import stops
        rows = self._parse_csv_from_zip(zip_path, 'stops.txt')
        for row in rows:
            try:
                lat = float(row.get('stop_lat')) if row.get('stop_lat') else None
                lon = float(row.get('stop_lon')) if row.get('stop_lon') else None
            except (ValueError, TypeError):
                continue
            
            self.db.execute(text("""
                INSERT INTO stops (stop_id, stop_code, stop_name, stop_desc, stop_lat, stop_lon, zone_id)
                VALUES (:stop_id, :stop_code, :stop_name, :stop_desc, :stop_lat, :stop_lon, :zone_id)
                ON CONFLICT (stop_id) DO UPDATE SET
                    stop_name = EXCLUDED.stop_name,
                    stop_lat = EXCLUDED.stop_lat,
                    stop_lon = EXCLUDED.stop_lon
            """), {
                'stop_id': str(row.get('stop_id', '')),
                'stop_code': row.get('stop_code'),
                'stop_name': row.get('stop_name', ''),
                'stop_desc': row.get('stop_desc'),
                'stop_lat': lat,
                'stop_lon': lon,
                'zone_id': row.get('zone_id')
            })
        stats['stops'] = len(rows)
        self.db.commit()
        
        # Import routes
        rows = self._parse_csv_from_zip(zip_path, 'routes.txt')
        for row in rows:
            try:
                route_type = int(row.get('route_type', 3))
            except (ValueError, TypeError):
                route_type = 3
            
            self.db.execute(text("""
                INSERT INTO routes (route_id, agency_id, route_short_name, route_long_name, 
                                  route_desc, route_type, route_color, route_text_color)
                VALUES (:route_id, :agency_id, :route_short_name, :route_long_name,
                       :route_desc, :route_type, :route_color, :route_text_color)
                ON CONFLICT (route_id) DO UPDATE SET
                    route_short_name = EXCLUDED.route_short_name,
                    route_long_name = EXCLUDED.route_long_name,
                    route_type = EXCLUDED.route_type
            """), {
                'route_id': str(row.get('route_id', '')),
                'agency_id': row.get('agency_id'),
                'route_short_name': row.get('route_short_name', ''),
                'route_long_name': row.get('route_long_name', ''),
                'route_desc': row.get('route_desc'),
                'route_type': route_type,
                'route_color': row.get('route_color'),
                'route_text_color': row.get('route_text_color')
            })
        stats['routes'] = len(rows)
        self.db.commit()
        
        # Import calendar
        rows = self._parse_csv_from_zip(zip_path, 'calendar.txt')
        for row in rows:
            self.db.execute(text("""
                INSERT INTO calendar (service_id, monday, tuesday, wednesday, thursday, 
                                     friday, saturday, sunday, start_date, end_date)
                VALUES (:service_id, :monday, :tuesday, :wednesday, :thursday,
                       :friday, :saturday, :sunday, :start_date, :end_date)
                ON CONFLICT (service_id) DO NOTHING
            """), {
                'service_id': row.get('service_id', ''),
                'monday': int(row.get('monday', 0)),
                'tuesday': int(row.get('tuesday', 0)),
                'wednesday': int(row.get('wednesday', 0)),
                'thursday': int(row.get('thursday', 0)),
                'friday': int(row.get('friday', 0)),
                'saturday': int(row.get('saturday', 0)),
                'sunday': int(row.get('sunday', 0)),
                'start_date': int(row.get('start_date', 0)),
                'end_date': int(row.get('end_date', 0))
            })
        stats['calendar'] = len(rows)
        self.db.commit()
        
        # Import calendar_dates
        rows = self._parse_csv_from_zip(zip_path, 'calendar_dates.txt')
        service_ids = set(row.get('service_id', '') for row in rows if row.get('service_id'))
        
        # Create dummy calendar entries for service_ids not in calendar
        for service_id in service_ids:
            self.db.execute(text("""
                INSERT INTO calendar (service_id, monday, tuesday, wednesday, thursday, 
                                     friday, saturday, sunday, start_date, end_date)
                VALUES (:service_id, 0, 0, 0, 0, 0, 0, 0, 20200101, 20991231)
                ON CONFLICT (service_id) DO NOTHING
            """), {'service_id': service_id})
        
        for row in rows:
            self.db.execute(text("""
                INSERT INTO calendar_dates (service_id, date, exception_type)
                VALUES (:service_id, :date, :exception_type)
                ON CONFLICT (service_id, date) DO NOTHING
            """), {
                'service_id': row.get('service_id', ''),
                'date': int(row.get('date', 0)),
                'exception_type': int(row.get('exception_type', 1))
            })
        stats['calendar_dates'] = len(rows)
        self.db.commit()
        
        # Import trips
        rows = self._parse_csv_from_zip(zip_path, 'trips.txt')
        for row in rows:
            self.db.execute(text("""
                INSERT INTO trips (trip_id, route_id, service_id, trip_headsign, 
                                 direction_id, shape_id, wheelchair_accessible, bikes_allowed)
                VALUES (:trip_id, :route_id, :service_id, :trip_headsign,
                       :direction_id, :shape_id, :wheelchair_accessible, :bikes_allowed)
                ON CONFLICT (trip_id) DO UPDATE SET
                    route_id = EXCLUDED.route_id,
                    service_id = EXCLUDED.service_id
            """), {
                'trip_id': str(row.get('trip_id', '')),
                'route_id': str(row.get('route_id', '')),
                'service_id': row.get('service_id', ''),
                'trip_headsign': row.get('trip_headsign', ''),
                'direction_id': int(row.get('direction_id', 0)) if row.get('direction_id') else None,
                'shape_id': row.get('shape_id'),
                'wheelchair_accessible': int(row.get('wheelchair_accessible', 0)) if row.get('wheelchair_accessible') else 0,
                'bikes_allowed': int(row.get('bikes_allowed', 0)) if row.get('bikes_allowed') else 0
            })
        stats['trips'] = len(rows)
        self.db.commit()
        
        # Import stop_times (batch for performance)
        rows = self._parse_csv_from_zip(zip_path, 'stop_times.txt')
        batch_size = 500
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            for row in batch:
                self.db.execute(text("""
                    INSERT INTO stop_times (trip_id, arrival_time, departure_time, stop_id,
                                          stop_sequence, stop_headsign, pickup_type, drop_off_type,
                                          shape_dist_traveled, timepoint)
                    VALUES (:trip_id, :arrival_time, :departure_time, :stop_id,
                           :stop_sequence, :stop_headsign, :pickup_type, :drop_off_type,
                           :shape_dist_traveled, :timepoint)
                    ON CONFLICT (trip_id, stop_sequence) DO NOTHING
                """), {
                    'trip_id': str(row.get('trip_id', '')),
                    'arrival_time': row.get('arrival_time', ''),
                    'departure_time': row.get('departure_time', ''),
                    'stop_id': str(row.get('stop_id', '')),
                    'stop_sequence': int(row.get('stop_sequence', 0)),
                    'stop_headsign': row.get('stop_headsign'),
                    'pickup_type': int(row.get('pickup_type', 0)) if row.get('pickup_type') else 0,
                    'drop_off_type': int(row.get('drop_off_type', 0)) if row.get('drop_off_type') else 0,
                    'shape_dist_traveled': float(row.get('shape_dist_traveled', 0)) if row.get('shape_dist_traveled') else None,
                    'timepoint': int(row.get('timepoint', 1)) if row.get('timepoint') else 1
                })
            self.db.commit()
        stats['stop_times'] = len(rows)
        
        # Import shapes (batch for performance)
        rows = self._parse_csv_from_zip(zip_path, 'shapes.txt')
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            for row in batch:
                self.db.execute(text("""
                    INSERT INTO shapes (shape_id, shape_pt_lat, shape_pt_lon, 
                                      shape_pt_sequence, shape_dist_traveled)
                    VALUES (:shape_id, :shape_pt_lat, :shape_pt_lon,
                           :shape_pt_sequence, :shape_dist_traveled)
                    ON CONFLICT (shape_id, shape_pt_sequence) DO NOTHING
                """), {
                    'shape_id': row.get('shape_id', ''),
                    'shape_pt_lat': float(row.get('shape_pt_lat', 0)),
                    'shape_pt_lon': float(row.get('shape_pt_lon', 0)),
                    'shape_pt_sequence': int(row.get('shape_pt_sequence', 0)),
                    'shape_dist_traveled': float(row.get('shape_dist_traveled', 0)) if row.get('shape_dist_traveled') else None
                })
            self.db.commit()
        stats['shapes'] = len(rows)
        
        logger.info(f"Imported GTFS for {city}: {stats}")
        return stats
    
    def _add_indexes(self):
        """Add performance indexes after import"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_stops_name ON stops(stop_name)",
            "CREATE INDEX IF NOT EXISTS idx_stops_coords ON stops(stop_lat, stop_lon)",
            "CREATE INDEX IF NOT EXISTS idx_routes_short_name ON routes(route_short_name)",
            "CREATE INDEX IF NOT EXISTS idx_trips_route ON trips(route_id)",
            "CREATE INDEX IF NOT EXISTS idx_trips_service ON trips(service_id)",
            "CREATE INDEX IF NOT EXISTS idx_stop_times_stop ON stop_times(stop_id)",
            "CREATE INDEX IF NOT EXISTS idx_stop_times_trip ON stop_times(trip_id)",
            "CREATE INDEX IF NOT EXISTS idx_stop_times_arrival ON stop_times(arrival_time)",
        ]
        
        for idx_sql in indexes:
            try:
                self.db.execute(text(idx_sql))
                self.db.commit()
            except Exception as e:
                logger.debug(f"Index may already exist: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get current database statistics"""
        tables = ['agency', 'stops', 'routes', 'trips', 'stop_times', 'calendar', 'shapes']
        stats = {}
        
        for table in tables:
            try:
                result = self.db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                stats[table] = result.scalar()
            except Exception:
                stats[table] = 0
        
        return stats
