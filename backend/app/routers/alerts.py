"""
Alerts Router - Transport alerts management endpoints
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TransportAlert

logger = logging.getLogger(__name__)
router = APIRouter()


class AlertCreate(BaseModel):
    """Schema for creating a transport alert"""
    title: str
    message: str
    severity: str = "info"  # info, warning, critical
    affected_routes: Optional[str] = None
    affected_stops: Optional[str] = None
    expires_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    """Schema for updating a transport alert"""
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    affected_routes: Optional[str] = None
    affected_stops: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


@router.get("/alerts")
async def get_alerts(
    active_only: bool = True,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all transport alerts, optionally filtered"""
    try:
        query = db.query(TransportAlert)
        
        if active_only:
            now = datetime.utcnow()
            query = query.filter(
                TransportAlert.is_active == True,
                (TransportAlert.expires_at == None) | (TransportAlert.expires_at > now)
            )
        
        if severity:
            query = query.filter(TransportAlert.severity == severity)
        
        # Order by severity (critical first) then by creation date
        alerts = query.order_by(
            TransportAlert.severity.desc(),
            TransportAlert.created_at.desc()
        ).all()
        
        return {
            "count": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity,
                    "affected_routes": alert.affected_routes,
                    "affected_stops": alert.affected_stops,
                    "is_active": alert.is_active,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                    "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = db.query(TransportAlert).filter(TransportAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    
    return {
        "id": alert.id,
        "title": alert.title,
        "message": alert.message,
        "severity": alert.severity,
        "affected_routes": alert.affected_routes,
        "affected_stops": alert.affected_stops,
        "is_active": alert.is_active,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
        "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
    }


@router.get("/alerts/stop/{stop_id}")
async def get_alerts_for_stop(stop_id: str, db: Session = Depends(get_db)):
    """Get active alerts that affect a specific stop"""
    try:
        now = datetime.utcnow()
        
        # Get all active alerts
        alerts = db.query(TransportAlert).filter(
            TransportAlert.is_active == True,
            (TransportAlert.expires_at == None) | (TransportAlert.expires_at > now)
        ).all()
        
        # Filter to alerts that affect this stop (or have no specific stops = global)
        relevant_alerts = []
        for alert in alerts:
            if not alert.affected_stops:
                # Global alert - affects all stops
                relevant_alerts.append(alert)
            elif stop_id in alert.affected_stops.split(','):
                # Specific to this stop
                relevant_alerts.append(alert)
        
        return {
            "count": len(relevant_alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity,
                    "affected_routes": alert.affected_routes
                }
                for alert in relevant_alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.post("/alerts")
async def create_alert(alert_data: AlertCreate, db: Session = Depends(get_db)):
    """Create a new transport alert"""
    try:
        # Validate severity
        valid_severities = ['info', 'warning', 'critical']
        if alert_data.severity not in valid_severities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
            )
        
        alert = TransportAlert(
            title=alert_data.title,
            message=alert_data.message,
            severity=alert_data.severity,
            affected_routes=alert_data.affected_routes,
            affected_stops=alert_data.affected_stops,
            expires_at=alert_data.expires_at,
            is_active=True
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Created alert {alert.id}: {alert.title} ({alert.severity})")
        
        return {
            "id": alert.id,
            "title": alert.title,
            "severity": alert.severity,
            "message": "Alert created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.put("/alerts/{alert_id}")
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing alert"""
    alert = db.query(TransportAlert).filter(TransportAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    
    try:
        # Update fields if provided
        if alert_data.title is not None:
            alert.title = alert_data.title
        if alert_data.message is not None:
            alert.message = alert_data.message
        if alert_data.severity is not None:
            valid_severities = ['info', 'warning', 'critical']
            if alert_data.severity not in valid_severities:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
                )
            alert.severity = alert_data.severity
        if alert_data.affected_routes is not None:
            alert.affected_routes = alert_data.affected_routes
        if alert_data.affected_stops is not None:
            alert.affected_stops = alert_data.affected_stops
        if alert_data.is_active is not None:
            alert.is_active = alert_data.is_active
        if alert_data.expires_at is not None:
            alert.expires_at = alert_data.expires_at
        
        db.commit()
        db.refresh(alert)
        
        return {
            "id": alert.id,
            "title": alert.title,
            "message": "Alert updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(TransportAlert).filter(TransportAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    
    try:
        db.delete(alert)
        db.commit()
        
        logger.info(f"Deleted alert {alert_id}")
        
        return {"message": f"Alert {alert_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")
