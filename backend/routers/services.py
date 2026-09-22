from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, Service, Department
from auth import get_current_user
from database import User

router = APIRouter()


@router.get("")
def list_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    result = []
    for s in services:
        result.append({
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "description": s.description,
            "department": s.department.name if s.department else "",
            "department_code": s.department.code if s.department else "",
            "required_departments": s.required_departments,
        })
    return result
