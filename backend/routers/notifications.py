from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Notification, Citizen
from auth import require_citizen
from database import User

router = APIRouter()


@router.get("")
def get_notifications(current_user: User = Depends(require_citizen), db: Session = Depends(get_db)):
    citizen = current_user.citizen
    if not citizen:
        return []
    notifs = db.query(Notification).filter(Notification.citizen_id == citizen.id).order_by(Notification.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "application_id": n.application_id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        }
        for n in notifs
    ]


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, current_user: User = Depends(require_citizen), db: Session = Depends(get_db)):
    citizen = current_user.citizen
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.citizen_id == citizen.id
    ).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "Marked as read."}


@router.post("/mark-all-read")
def mark_all_read(current_user: User = Depends(require_citizen), db: Session = Depends(get_db)):
    citizen = current_user.citizen
    db.query(Notification).filter(Notification.citizen_id == citizen.id).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read."}
