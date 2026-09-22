from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, Application, ApplicationStep, Service, Citizen, Notification, AuditLog, Consent, Department
from auth import get_current_user, require_citizen, require_officer
from database import User
from datetime import datetime
import httpx

router = APIRouter()


class ApplicationCreate(BaseModel):
    service_code: str
    form_data: dict = {}


def get_workflow_steps(service: Service):
    """Return ordered workflow steps based on service type."""
    code = service.code
    dept_map = {
        "PROP_TRANSFER": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Revenue Property Verification", "dept": "REVENUE"},
            {"name": "Municipal Property Verification", "dept": "MUNICIPAL"},
            {"name": "Revenue Final Approval", "dept": "REVENUE"},
            {"name": "Citizen Notification", "dept": "SANYUKT"},
        ],
        "PROP_CERT": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Revenue Verification", "dept": "REVENUE"},
            {"name": "Certificate Issue", "dept": "REVENUE"},
        ],
        "INCOME_CERT": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Revenue Income Verification", "dept": "REVENUE"},
            {"name": "Certificate Issue", "dept": "REVENUE"},
        ],
        "DOMICILE_CERT": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Revenue Domicile Verification", "dept": "REVENUE"},
            {"name": "Certificate Issue", "dept": "REVENUE"},
        ],
        "BLDG_PERMISSION": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Municipal Site Verification", "dept": "MUNICIPAL"},
            {"name": "Revenue NOC", "dept": "REVENUE"},
            {"name": "Final Approval", "dept": "MUNICIPAL"},
        ],
        "WATER_CONN": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Municipal Property Verification", "dept": "MUNICIPAL"},
            {"name": "Connection Approved", "dept": "MUNICIPAL"},
        ],
        "BIRTH_CERT": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Municipal Record Verification", "dept": "MUNICIPAL"},
            {"name": "Certificate Issue", "dept": "MUNICIPAL"},
        ],
        "SCHOLARSHIP": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Revenue Income Verification", "dept": "REVENUE"},
            {"name": "Welfare Eligibility Check", "dept": "WELFARE"},
            {"name": "Scholarship Approved", "dept": "WELFARE"},
        ],
        "WELFARE_SCHEME": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Welfare Eligibility Check", "dept": "WELFARE"},
            {"name": "Enrollment Completed", "dept": "WELFARE"},
        ],
        "CASTE_CERT": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Revenue Caste Record Scrutiny", "dept": "REVENUE"},
            {"name": "Welfare Social Status Clearance", "dept": "WELFARE"},
            {"name": "Caste Certificate Issuance", "dept": "REVENUE"},
        ],
        "NON_CREAMY": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "3-Year Revenue Assessment", "dept": "REVENUE"},
            {"name": "Certificate Issue", "dept": "REVENUE"},
        ],
        "TRADE_LICENSE": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Municipal Ward Inspection", "dept": "MUNICIPAL"},
            {"name": "Health & Fire NOC", "dept": "MUNICIPAL"},
            {"name": "License Issued", "dept": "MUNICIPAL"},
        ],
        "PROP_TAX": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Municipal Property Extract Search", "dept": "MUNICIPAL"},
            {"name": "Tax Dues Clearance & Assessment Copy", "dept": "MUNICIPAL"},
        ],
        "DIVYANG_AID": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "UDID Medical Disability Verification", "dept": "WELFARE"},
            {"name": "Subsidy Sanction Approved", "dept": "WELFARE"},
        ],
        "GRAM_NOC": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Gram Sevak Assessment Form 8", "dept": "REVENUE"},
            {"name": "Panchayat NOC Issued", "dept": "REVENUE"},
        ],
        "HEALTH_CARD": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Ration & Revenue Income Verification", "dept": "REVENUE"},
            {"name": "MJPJAY E-Card Generation", "dept": "SANYUKT"},
        ],
        "KRISHI_SUBSIDY": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "7/12 Land Holding Verification", "dept": "REVENUE"},
            {"name": "Krishi Yantra Subsidy Sanctioned", "dept": "REVENUE"},
        ],
        "BOCW_REG": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "90-Day Construction Work Verification", "dept": "MUNICIPAL"},
            {"name": "BOCW Smart Card Issued", "dept": "SANYUKT"},
        ],
        "SHOP_EST": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Commercial Zone Municipal Check", "dept": "MUNICIPAL"},
            {"name": "Gumasta Certificate Issued", "dept": "MUNICIPAL"},
        ],
        "FEES_CONCESSION": [
            {"name": "Identity Verification", "dept": "SANYUKT"},
            {"name": "Income & Domicile Verification", "dept": "REVENUE"},
            {"name": "DBT Fee Reimbursement Approved", "dept": "WELFARE"},
        ],
    }
    return dept_map.get(code, [{"name": "Identity Verification", "dept": "SANYUKT"}, {"name": "Departmental Scrutiny", "dept": "REVENUE"}, {"name": "Digital Issuance", "dept": "SANYUKT"}])


@router.post("")
def create_application(
    req: ApplicationCreate,
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    citizen = current_user.citizen
    if not citizen:
        raise HTTPException(status_code=400, detail="Citizen profile not found.")

    service = db.query(Service).filter(Service.code == req.service_code).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    # Generate application ID
    count = db.query(Application).count() + 1
    year = datetime.utcnow().year
    app_id = f"SYN-{year}-{count:03d}"

    app = Application(
        application_id=app_id,
        citizen_id=citizen.id,
        service_id=service.id,
        status="SUBMITTED",
        current_step=0,
        form_data=req.form_data,
    )
    db.add(app)
    db.flush()

    # Create workflow steps
    steps_def = get_workflow_steps(service)
    for i, s in enumerate(steps_def, start=1):
        db.add(ApplicationStep(
            application_id=app.id,
            step_number=i,
            step_name=s["name"],
            department=s["dept"],
            status="PENDING"
        ))

    # Notification
    db.add(Notification(
        citizen_id=citizen.id,
        application_id=app_id,
        title=f"Application Received — {service.name}",
        message=f"Your application for {service.name} has been received. Application ID: {app_id}."
    ))

    db.add(AuditLog(
        user_identifier=citizen.full_name,
        system="Sanyukt",
        action=f"Application Submitted — {service.name}",
        application_id=app_id,
        status="SUCCESS"
    ))

    db.commit()
    return {"application_id": app_id, "status": "SUBMITTED", "message": "Application submitted successfully."}


@router.get("")
def list_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role in ("officer", "admin"):
        apps = db.query(Application).order_by(Application.created_at.desc()).all()
    else:
        citizen = current_user.citizen
        if not citizen:
            return []
        apps = db.query(Application).filter(Application.citizen_id == citizen.id).order_by(Application.created_at.desc()).all()

    result = []
    for a in apps:
        c = db.query(Citizen).filter(Citizen.id == a.citizen_id).first()
        result.append({
            "application_id": a.application_id,
            "service": a.service.name if a.service else "",
            "department": a.service.department.name if a.service and a.service.department else "",
            "status": a.status,
            "citizen_name": c.full_name if c else "",
            "sanyukt_id": c.sanyukt_id if c else "",
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            "current_step": a.current_step,
        })
    return result


@router.get("/{application_id}")
def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    if current_user.role == "citizen":
        citizen = current_user.citizen
        if not citizen or app.citizen_id != citizen.id:
            raise HTTPException(status_code=403, detail="Access denied.")

    c = db.query(Citizen).filter(Citizen.id == app.citizen_id).first()
    steps = []
    for s in app.steps:
        steps.append({
            "step_number": s.step_number,
            "step_name": s.step_name,
            "department": s.department,
            "status": s.status,
            "result_data": s.result_data or {},
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "error_message": s.error_message,
            "retry_count": s.retry_count,
        })

    consents = db.query(Consent).filter(
        Consent.citizen_id == (c.id if c else 0),
        Consent.application_id == application_id
    ).all()

    return {
        "application_id": app.application_id,
        "service": app.service.name if app.service else "",
        "service_code": app.service.code if app.service else "",
        "department": app.service.department.name if app.service and app.service.department else "",
        "status": app.status,
        "current_step": app.current_step,
        "form_data": app.form_data or {},
        "created_at": app.created_at.isoformat(),
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
        "citizen_name": c.full_name if c else "",
        "sanyukt_id": c.sanyukt_id if c else "",
        "citizen_mobile": c.mobile if c else "",
        "district": c.district if c else "",
        "steps": steps,
        "consents": [{"department": co.department_code, "data_types": co.data_types, "granted": co.granted} for co in consents],
    }


@router.post("/{application_id}/process")
def process_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger interoperability processing for an application."""
    from routers.interoperability import run_workflow
    result = run_workflow(application_id, db)
    return result
