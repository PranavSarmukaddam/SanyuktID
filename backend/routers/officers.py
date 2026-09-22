from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Application, ApplicationStep, Department, ApiLog, AuditLog, Citizen, Notification
from auth import require_officer
from database import User

router = APIRouter()


@router.get("/stats")
def officer_stats(db: Session = Depends(get_db), current_user: User = Depends(require_officer)):
    total = db.query(Application).count()
    pending = db.query(Application).filter(Application.status == "SUBMITTED").count()
    in_progress = db.query(Application).filter(Application.status == "IN_PROGRESS").count()
    on_hold = db.query(Application).filter(Application.status == "ON_HOLD").count()
    completed = db.query(Application).filter(Application.status == "COMPLETED").count()
    failed = db.query(Application).filter(Application.status == "FAILED").count()

    # Failed integrations = steps with FAILED status
    failed_steps = db.query(ApplicationStep).filter(ApplicationStep.status == "FAILED").count()

    # Department activity
    rev_calls = db.query(ApiLog).filter(ApiLog.target_system == "REVENUE").count()
    mun_calls = db.query(ApiLog).filter(ApiLog.target_system == "MUNICIPAL").count()
    wel_calls = db.query(ApiLog).filter(ApiLog.target_system == "WELFARE").count()

    # Department health
    depts = db.query(Department).all()
    dept_health = [
        {"code": d.code, "name": d.name, "health": "DEGRADED" if d.failure_mode else "OK", "failure_mode": d.failure_mode}
        for d in depts
    ]

    # Recent notifications
    recent_notifs = db.query(Notification).order_by(Notification.created_at.desc()).limit(5).all()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "on_hold": on_hold,
        "completed": completed,
        "failed": failed,
        "failed_integrations": failed_steps,
        "department_activity": {
            "REVENUE": rev_calls,
            "MUNICIPAL": mun_calls,
            "WELFARE": wel_calls,
        },
        "department_health": dept_health,
    }
