"""
SQLAlchemy models for Bus Hackaton application
Includes GTFS models and display-specific models
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DECIMAL, Boolean,
    ForeignKey, Index, DateTime, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


# =============================================================================
# GTFS Models
# =============================================================================

class Agency(Base):
    """GTFS Agency table"""
    __tablename__ = 'agency'
    
    agency_id = Column(Text, primary_key=True)
    agency_name = Column(Text, nullable=False)
    agency_url = Column(Text, nullable=False)
    agency_timezone = Column(Text, nullable=False)
    agency_lang = Column(Text)
    
    routes = relationship("Route", back_populates="agency")


class Stop(Base):
    """GTFS Stops table"""
    __tablename__ = 'stops'
    
    stop_id = Column(Text, primary_key=True)
    stop_code = Column(Text)
    stop_name = Column(Text)
    stop_desc = Column(Text)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(Text)
    stop_url = Column(Text)
    location_type = Column(Integer, default=0)
    parent_station = Column(Text)
    wheelchair_boarding = Column(Integer, default=0)
    
    stop_times = relationship("StopTime", back_populates="stop")


class Route(Base):
    """GTFS Routes table"""
    __tablename__ = 'routes'
    
    route_id = Column(Text, primary_key=True)
    agency_id = Column(Text, ForeignKey('agency.agency_id'))
    route_short_name = Column(Text)
    route_long_name = Column(Text)
    route_desc = Column(Text)
    route_type = Column(Integer, nullable=False)
    route_color = Column(Text)
    route_text_color = Column(Text)
    route_sort_order = Column(Integer)
    
    agency = relationship("Agency", back_populates="routes")


class Calendar(Base):
    """GTFS Calendar table"""
    __tablename__ = 'calendar'
    
    service_id = Column(Text, primary_key=True)
    monday = Column(Integer, nullable=False)
    tuesday = Column(Integer, nullable=False)
    wednesday = Column(Integer, nullable=False)
    thursday = Column(Integer, nullable=False)
    friday = Column(Integer, nullable=False)
    saturday = Column(Integer, nullable=False)
    sunday = Column(Integer, nullable=False)
    start_date = Column(Integer, nullable=False)
    end_date = Column(Integer, nullable=False)
    
    trips = relationship("Trip", back_populates="calendar")
    calendar_dates = relationship("CalendarDate", back_populates="calendar")


class CalendarDate(Base):
    """GTFS Calendar Dates table"""
    __tablename__ = 'calendar_dates'
    
    service_id = Column(Text, ForeignKey('calendar.service_id'), primary_key=True)
    date = Column(Integer, primary_key=True)
    exception_type = Column(Integer)
    
    calendar = relationship("Calendar", back_populates="calendar_dates")


class Shape(Base):
    """GTFS Shapes table"""
    __tablename__ = 'shapes'
    
    shape_id = Column(Text, primary_key=True)
    shape_pt_lat = Column(Float, nullable=False)
    shape_pt_lon = Column(Float, nullable=False)
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Float)
    
    __table_args__ = (
        Index('idx_shapes_shape_id', 'shape_id'),
    )


class Trip(Base):
    """GTFS Trips table"""
    __tablename__ = 'trips'
    
    trip_id = Column(Text, primary_key=True)
    route_id = Column(Text, nullable=False)
    service_id = Column(Text, ForeignKey('calendar.service_id'), nullable=False)
    trip_headsign = Column(Text)
    trip_short_name = Column(Text)
    direction_id = Column(Integer)
    block_id = Column(Text)
    shape_id = Column(Text)
    wheelchair_accessible = Column(Integer, default=0)
    bikes_allowed = Column(Integer, default=0)
    
    calendar = relationship("Calendar", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip", order_by="StopTime.stop_sequence")
    
    __table_args__ = (
        Index('idx_trips_route_id', 'route_id'),
        Index('idx_trips_service_id', 'service_id'),
    )


class StopTime(Base):
    """GTFS Stop Times table"""
    __tablename__ = 'stop_times'
    
    trip_id = Column(Text, ForeignKey('trips.trip_id'), primary_key=True)
    arrival_time = Column(Text)
    departure_time = Column(Text)
    stop_id = Column(Text, ForeignKey('stops.stop_id'), nullable=False)
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(Text)
    pickup_type = Column(Integer, default=0)
    drop_off_type = Column(Integer, default=0)
    shape_dist_traveled = Column(Float)
    timepoint = Column(Integer, default=1)
    
    trip = relationship("Trip", back_populates="stop_times")
    stop = relationship("Stop", back_populates="stop_times")
    
    __table_args__ = (
        Index('idx_stop_times_trip_id', 'trip_id'),
        Index('idx_stop_times_stop_id', 'stop_id'),
    )


class FareAttribute(Base):
    """GTFS Fare Attributes table"""
    __tablename__ = 'fare_attributes'
    
    fare_id = Column(Text, primary_key=True)
    price = Column(DECIMAL(10, 2))
    currency_type = Column(Text)
    payment_method = Column(Integer)
    transfers = Column(Integer)
    agency_id = Column(Text)
    transfer_duration = Column(Integer)
    
    fare_rules = relationship("FareRule", back_populates="fare_attribute")


class FareRule(Base):
    """GTFS Fare Rules table"""
    __tablename__ = 'fare_rules'
    
    fare_id = Column(Text, ForeignKey('fare_attributes.fare_id'), primary_key=True)
    route_id = Column(Text, primary_key=True)
    origin_id = Column(Text)
    destination_id = Column(Text)
    
    fare_attribute = relationship("FareAttribute", back_populates="fare_rules")


# =============================================================================
# Display-specific Models
# =============================================================================

class AlertSeverity(enum.Enum):
    """Severity levels for transport alerts"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Ad(Base):
    """Advertisement content for digital displays"""
    __tablename__ = 'ads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    image_url = Column(Text, nullable=False)  # Path to uploaded image
    link_url = Column(Text)  # Optional click-through URL
    advertiser_name = Column(String(255))  # Business name
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)  # For manual ordering
    duration_seconds = Column(Integer, default=10)  # How long to show
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiration
    
    __table_args__ = (
        Index('idx_ads_active', 'is_active'),
        Index('idx_ads_expires', 'expires_at'),
    )


class GovernmentNews(Base):
    """Government news/announcements for digital displays - bilingual support"""
    __tablename__ = 'government_news'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Greek content (primary)
    title_el = Column(String(255), nullable=False)  # Greek title
    content_el = Column(Text, nullable=False)  # Greek content
    # English content
    title_en = Column(String(255))  # English title
    content_en = Column(Text)  # English content
    image_url = Column(Text)  # Optional image
    source = Column(String(255))  # e.g., "Ministry of Transport"
    duration_seconds = Column(Integer, default=12)  # How long to show
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_news_active', 'is_active'),
        Index('idx_news_expires', 'expires_at'),
    )


class TransportAlert(Base):
    """Transport alerts for bus arrival displays"""
    __tablename__ = 'transport_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default='info', nullable=False)  # info, warning, critical
    affected_routes = Column(Text)  # Comma-separated route IDs or names
    affected_stops = Column(Text)  # Comma-separated stop IDs
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_alerts_active', 'is_active'),
        Index('idx_alerts_severity', 'severity'),
        Index('idx_alerts_expires', 'expires_at'),
    )
