"""
Database connection and query utilities using SQLAlchemy
"""
import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv(override=False)

logger = logging.getLogger(__name__)

# SQLAlchemy engine
engine = None
SessionLocal = None


def get_database_url() -> str:
    """Build database URL from environment variables"""
    # Use postgresql+psycopg for psycopg3 driver
    return (
        f"postgresql+psycopg://{os.getenv('DB_USER', 'signage')}:{os.getenv('DB_PASSWORD', 'signage_password')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 5433)}"
        f"/{os.getenv('DB_DATABASE', 'bus_signage')}"
    )


def get_engine():
    """Create or return existing SQLAlchemy engine"""
    global engine
    
    if engine is None:
        database_url = get_database_url()
        
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
        logger.info("SQLAlchemy engine created")
    
    return engine


def get_session_factory():
    """Get or create session factory"""
    global SessionLocal
    
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False
        )
    
    return SessionLocal


@contextmanager
def get_db_session():
    """
    Context manager for database sessions
    
    Usage:
        with get_db_session() as session:
            result = session.query(Stop).filter_by(stop_id='123').first()
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """
    Dependency for FastAPI endpoints
    
    Usage in FastAPI:
        @app.get("/api/stops")
        def get_stops(db: Session = Depends(get_db)):
            return db.query(Stop).all()
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from app.models import Base
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables created")


def test_connection() -> bool:
    """Test database connection"""
    try:
        with get_db_session() as session:
            result = session.execute(text("SELECT NOW()"))
            row = result.fetchone()
            logger.info(f"Database connection successful: {row[0]}")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
