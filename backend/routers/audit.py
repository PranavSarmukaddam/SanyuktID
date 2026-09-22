from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db, AuditLog, ApiLog
from auth import get_current_user
from database import User
from typing import Optional

router = APIRouter()


@router.get("")
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    application_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if application_id:
        q = q.filter(AuditLog.application_id == application_id)
    logs = q.offset(skip).limit(limit).all()
    return [
        {
            "id": l.id,
            "timestamp": l.timestamp.isoformat(),
            "user_identifier": l.user_identifier,
            "system": l.system,
            "action": l.action,
            "application_id": l.application_id,
            "status": l.status,
            "details": l.details or {}
        }
        for l in logs
    ]


@router.get("/api-logs")
def get_api_logs(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs = db.query(ApiLog).order_by(ApiLog.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": l.id,
            "timestamp": l.timestamp.isoformat(),
            "source_system": l.source_system,
            "target_system": l.target_system,
            "endpoint": l.endpoint,
            "method": l.method,
            "status_code": l.status_code,
            "duration_ms": l.duration_ms,
            "application_id": l.application_id,
        }
        for l in logs
    ]
