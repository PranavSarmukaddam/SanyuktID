from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db, Consent, Citizen, AuditLog, Application
from auth import require_citizen, get_current_user
from database import User
from datetime import datetime

router = APIRouter()


class ConsentGrant(BaseModel):
    application_id: str
    department_code: str
    data_types: str  # comma-separated


class ConsentRevoke(BaseModel):
    application_id: str
    department_code: str


@router.post("")
def grant_consent(
    req: ConsentGrant,
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    citizen = current_user.citizen
    if not citizen:
        raise HTTPException(status_code=400, detail="Citizen profile not found.")

    # Check if consent already exists
    existing = db.query(Consent).filter(
        Consent.citizen_id == citizen.id,
        Consent.application_id == req.application_id,
        Consent.department_code == req.department_code
    ).first()

    if existing:
        existing.granted = True
        existing.data_types = req.data_types
        existing.granted_at = datetime.utcnow()
    else:
        db.add(Consent(
            citizen_id=citizen.id,
            application_id=req.application_id,
            department_code=req.department_code,
            data_types=req.data_types,
            granted=True
        ))

    db.add(AuditLog(
        user_identifier=citizen.full_name,
        system="Sanyukt",
        action=f"Consent Granted — {req.department_code} ({req.application_id})",
        application_id=req.application_id,
        status="SUCCESS",
        details={"data_types": req.data_types}
    ))
    db.commit()
    return {"message": "Consent granted.", "department_code": req.department_code}


@router.delete("")
def revoke_consent(
    req: ConsentRevoke,
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    citizen = current_user.citizen
    existing = db.query(Consent).filter(
        Consent.citizen_id == citizen.id,
        Consent.application_id == req.application_id,
        Consent.department_code == req.department_code
    ).first()
    if existing:
        existing.granted = False
        db.add(AuditLog(
            user_identifier=citizen.full_name,
            system="Sanyukt",
            action=f"Consent Revoked — {req.department_code} ({req.application_id})",
            application_id=req.application_id,
            status="SUCCESS"
        ))
        db.commit()
    return {"message": "Consent revoked."}


@router.get("")
def list_consents(
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    citizen = current_user.citizen
    if not citizen:
        return []
    consents = db.query(Consent).filter(Consent.citizen_id == citizen.id).order_by(Consent.granted_at.desc()).all()
    return [
        {
            "id": c.id,
            "application_id": c.application_id,
            "department_code": c.department_code,
            "data_types": c.data_types,
            "granted": c.granted,
            "granted_at": c.granted_at.isoformat() if c.granted_at else None
        }
        for c in consents
    ]


def check_consent(citizen_id: int, application_id: str, department_code: str, db: Session) -> bool:
    consent = db.query(Consent).filter(
        Consent.citizen_id == citizen_id,
        Consent.application_id == application_id,
        Consent.department_code == department_code,
        Consent.granted == True
    ).first()
    return consent is not None
