from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Department, Application, ApplicationStep, ApiLog
from auth import get_current_user, require_officer
from database import User

router = APIRouter()


@router.get("/status")
def department_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    depts = db.query(Department).all()
    result = []
    for d in depts:
        api_call_count = db.query(ApiLog).filter(ApiLog.target_system == d.code).count()
        failed_count = db.query(ApiLog).filter(ApiLog.target_system == d.code, ApiLog.status_code >= 400).count()
        result.append({
            "code": d.code,
            "name": d.name,
            "api_base_url": d.api_base_url,
            "is_active": d.is_active,
            "failure_mode": d.failure_mode,
            "total_api_calls": api_call_count,
            "failed_calls": failed_count,
            "health": "DEGRADED" if d.failure_mode else "OK",
        })
    return result


class FailureModeRequest(BaseModel):
    department_code: str
    failure_mode: bool


@router.post("/failure-mode")
def toggle_failure_mode(
    req: FailureModeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    dept = db.query(Department).filter(Department.code == req.department_code).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    dept.failure_mode = req.failure_mode
    db.commit()
    return {"message": f"Failure mode {'enabled' if req.failure_mode else 'disabled'} for {dept.name}."}


@router.get("")
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    depts = db.query(Department).all()
    return [{"id": d.id, "code": d.code, "name": d.name, "failure_mode": d.failure_mode} for d in depts]
