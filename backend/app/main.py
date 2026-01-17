"""
Bus Signage Backend - FastAPI Application
Main application entry point with API endpoints
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import database and routers
from app.database import init_db, test_connection
from app.routers import stops, arrivals, ads, news, alerts, gtfs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Bus Signage Backend...")
    
    # Test database connection
    if test_connection():
        logger.info("Database connection successful")
        # Initialize database tables
        init_db()
    else:
        logger.warning("Database connection failed - some features may not work")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bus Signage Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="Bus Signage API",
    description="API for bus stop digital signage system - arrivals, ads, news, and alerts",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - allow all origins for prototype
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(stops.router, prefix="/api", tags=["Stops"])
app.include_router(arrivals.router, prefix="/api", tags=["Arrivals"])
app.include_router(ads.router, prefix="/api", tags=["Ads"])
app.include_router(news.router, prefix="/api", tags=["News"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(gtfs.router, prefix="/api", tags=["GTFS"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "Bus Signage API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "stops": "/api/stops",
            "arrivals": "/api/arrivals/{stop_id}",
            "ads": "/api/ads",
            "news": "/api/news",
            "alerts": "/api/alerts",
            "content": "/api/content",
            "gtfs": {
                "cities": "/api/gtfs/cities",
                "download": "/api/gtfs/download",
                "import": "/api/gtfs/import",
                "sync": "/api/gtfs/sync",
                "stats": "/api/gtfs/stats"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_ok = test_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected"
    }


@app.get("/api/content")
async def get_all_content():
    """
    Get all active content for display screens.
    Returns ads, news, and alerts in a single response.
    """
    from app.database import get_db_session
    from app.models import Ad, GovernmentNews, TransportAlert
    from datetime import datetime
    
    with get_db_session() as db:
        now = datetime.utcnow()
        
        # Get active ads (not expired)
        ads_query = db.query(Ad).filter(
            Ad.is_active == True,
            (Ad.expires_at == None) | (Ad.expires_at > now)
        ).order_by(Ad.display_order, Ad.created_at.desc()).all()
        
        # Get active news (not expired)
        news_query = db.query(GovernmentNews).filter(
            GovernmentNews.is_active == True,
            (GovernmentNews.expires_at == None) | (GovernmentNews.expires_at > now)
        ).order_by(GovernmentNews.display_order, GovernmentNews.created_at.desc()).all()
        
        # Get active alerts (not expired)
        alerts_query = db.query(TransportAlert).filter(
            TransportAlert.is_active == True,
            (TransportAlert.expires_at == None) | (TransportAlert.expires_at > now)
        ).order_by(TransportAlert.severity.desc(), TransportAlert.created_at.desc()).all()
        
        return {
            "ads": [
                {
                    "id": ad.id,
                    "title": ad.title,
                    "image_url": ad.image_url,
                    "link_url": ad.link_url,
                    "advertiser_name": ad.advertiser_name,
                    "duration_seconds": ad.duration_seconds
                }
                for ad in ads_query
            ],
            "news": [
                {
                    "id": item.id,
                    "title_el": item.title_el,
                    "content_el": item.content_el,
                    "title_en": item.title_en,
                    "content_en": item.content_en,
                    "image_url": item.image_url,
                    "source": item.source,
                    "duration_seconds": item.duration_seconds
                }
                for item in news_query
            ],
            "alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity,
                    "affected_routes": alert.affected_routes,
                    "affected_stops": alert.affected_stops
                }
                for alert in alerts_query
            ]
        }
