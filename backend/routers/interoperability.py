"""
Interoperability layer — department connectors, data mapping, workflow engine.
"""
import httpx
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Application, ApplicationStep, Citizen, Department, Notification, AuditLog, ApiLog, Consent
from auth import get_current_user
from database import User

router = APIRouter()

# --- Data Mapping ---
FIELD_MAP = {
    "owner_name": "citizen_name",
    "property_owner": "citizen_name",
    "application_no": "application_id",
}


def map_data(data: dict) -> dict:
    """Map department-specific field names to common field names."""
    mapped = {}
    for k, v in data.items():
        mapped[FIELD_MAP.get(k, k)] = v
    return mapped


# --- Connectors ---
def call_department(dept: Department, endpoint: str, payload: dict, db: Session, application_id: str = None) -> dict:
    """Generic department API caller with logging and retry."""
    start = time.time()
    url = f"{dept.api_base_url}{endpoint}"
    status_code = None
    response_data = {}
    error = None

    if dept.failure_mode:
        # Simulate failure
        duration_ms = int((time.time() - start) * 1000)
        db.add(ApiLog(
            source_system="Sanyukt",
            target_system=dept.code,
            endpoint=endpoint,
            method="POST",
            request_data=payload,
            response_data={"error": "Service unavailable (simulated failure)"},
            status_code=503,
            duration_ms=duration_ms,
            application_id=application_id
        ))
        db.add(AuditLog(
            user_identifier="Sanyukt",
            system=dept.name,
            action=f"API Call — {endpoint} (FAILURE - simulated)",
            application_id=application_id,
            status="FAILED",
            details={"error": "Service unavailable"}
        ))
        db.commit()
        raise HTTPException(status_code=503, detail=f"{dept.name} is temporarily unavailable. Your application has been saved and processing will continue once the department system is available.")

    for attempt in range(1, 3):
        try:
            resp = httpx.post(url, json=payload, timeout=10.0)
            status_code = resp.status_code
            response_data = resp.json()
            break
        except Exception as e:
            error = str(e)
            if attempt < 2:
                time.sleep(1)

    duration_ms = int((time.time() - start) * 1000)

    db.add(ApiLog(
        source_system="Sanyukt",
        target_system=dept.code,
        endpoint=endpoint,
        method="POST",
        request_data=payload,
        response_data=response_data if not error else {"error": error},
        status_code=status_code or 500,
        duration_ms=duration_ms,
        application_id=application_id
    ))
    db.add(AuditLog(
        user_identifier="Sanyukt",
        system=dept.name,
        action=f"API Call — {endpoint}",
        application_id=application_id,
        status="SUCCESS" if status_code and 200 <= status_code < 300 else "FAILED",
        details=response_data
    ))
    db.commit()

    if error:
        raise HTTPException(status_code=503, detail=f"Could not connect to {dept.name}. Please try again later.")

    return map_data(response_data)


# --- Revenue Connector ---
class RevenueConnector:
    def __init__(self, dept: Department, db: Session):
        self.dept = dept
        self.db = db

    def verify_property(self, application_id: str, citizen_id: str, property_id: str) -> dict:
        return call_department(
            self.dept,
            "/api/revenue/property/verify",
            {"application_id": application_id, "citizen_id": citizen_id, "property_id": property_id},
            self.db,
            application_id
        )

    def verify_income(self, application_id: str, citizen_id: str) -> dict:
        return call_department(
            self.dept,
            "/api/revenue/income/verify",
            {"application_id": application_id, "citizen_id": citizen_id},
            self.db,
            application_id
        )

    def issue_certificate(self, application_id: str, citizen_id: str, cert_type: str) -> dict:
        return call_department(
            self.dept,
            "/api/revenue/certificate/issue",
            {"application_id": application_id, "citizen_id": citizen_id, "cert_type": cert_type},
            self.db,
            application_id
        )

    def get_status(self, application_id: str) -> dict:
        return call_department(
            self.dept,
            "/api/revenue/status",
            {"application_id": application_id},
            self.db,
            application_id
        )


# --- Municipal Connector ---
class MunicipalConnector:
    def __init__(self, dept: Department, db: Session):
        self.dept = dept
        self.db = db

    def verify_property(self, application_id: str, property_id: str) -> dict:
        return call_department(
            self.dept,
            "/api/municipal/property/verify",
            {"application_id": application_id, "property_id": property_id},
            self.db,
            application_id
        )

    def verify_site(self, application_id: str, property_id: str) -> dict:
        return call_department(
            self.dept,
            "/api/municipal/site/verify",
            {"application_id": application_id, "property_id": property_id},
            self.db,
            application_id
        )

    def approve(self, application_id: str) -> dict:
        return call_department(
            self.dept,
            "/api/municipal/approve",
            {"application_id": application_id},
            self.db,
            application_id
        )


# --- Welfare Connector ---
class WelfareConnector:
    def __init__(self, dept: Department, db: Session):
        self.dept = dept
        self.db = db

    def check_eligibility(self, application_id: str, citizen_id: str, scheme_code: str) -> dict:
        return call_department(
            self.dept,
            "/api/welfare/eligibility/check",
            {"application_id": application_id, "citizen_id": citizen_id, "scheme_id": scheme_code},
            self.db,
            application_id
        )


# --- Workflow Engine ---
def run_workflow(application_id: str, db: Session) -> dict:
    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    if app.status == "COMPLETED":
        return {"message": "Application already completed.", "status": "COMPLETED"}

    citizen = db.query(Citizen).filter(Citizen.id == app.citizen_id).first()
    rev_dept = db.query(Department).filter(Department.code == "REVENUE").first()
    mun_dept = db.query(Department).filter(Department.code == "MUNICIPAL").first()
    wel_dept = db.query(Department).filter(Department.code == "WELFARE").first()

    steps = sorted(app.steps, key=lambda s: s.step_number)
    service_code = app.service.code if app.service else ""

    for step in steps:
        if step.status == "COMPLETED":
            continue
        if step.status == "FAILED":
            # Retry once
            step.retry_count = (step.retry_count or 0) + 1
            if step.retry_count > 2:
                app.status = "FAILED"
                db.commit()
                return {"message": "Application processing failed after retries.", "status": "FAILED"}

        step.status = "IN_PROGRESS"
        step.started_at = datetime.utcnow()
        app.status = "IN_PROGRESS"
        app.current_step = step.step_number
        db.commit()

        try:
            result = {}
            dept = step.department

            if dept == "SANYUKT":
                # Identity verification — always succeeds locally
                result = {"verified": True, "citizen_name": citizen.full_name, "sanyukt_id": citizen.sanyukt_id}

            elif dept == "REVENUE":
                rev = RevenueConnector(rev_dept, db)
                prop_id = (app.form_data or {}).get("property_id", "PROP-10291")
                if "Property" in step.step_name or "NOC" in step.step_name or "Final" in step.step_name:
                    result = rev.verify_property(application_id, citizen.sanyukt_id, prop_id)
                elif "Income" in step.step_name:
                    result = rev.verify_income(application_id, citizen.sanyukt_id)
                elif "Certificate" in step.step_name or "Domicile" in step.step_name:
                    result = rev.issue_certificate(application_id, citizen.sanyukt_id, service_code)
                else:
                    result = rev.verify_property(application_id, citizen.sanyukt_id, prop_id)

            elif dept == "MUNICIPAL":
                mun = MunicipalConnector(mun_dept, db)
                prop_id = (app.form_data or {}).get("property_id", "PROP-10291")
                if "Site" in step.step_name:
                    result = mun.verify_site(application_id, prop_id)
                elif "Approval" in step.step_name or "Approved" in step.step_name:
                    result = mun.approve(application_id)
                else:
                    result = mun.verify_property(application_id, prop_id)

            elif dept == "WELFARE":
                wel = WelfareConnector(wel_dept, db)
                scheme = "SCHOLAR-01" if "Scholarship" in service_code.upper() else "WELFARE-01"
                result = wel.check_eligibility(application_id, citizen.sanyukt_id, scheme)

            step.status = "COMPLETED"
            step.completed_at = datetime.utcnow()
            step.result_data = result
            db.commit()

        except HTTPException as e:
            step.status = "FAILED"
            step.error_message = e.detail
            app.status = "ON_HOLD"
            db.add(Notification(
                citizen_id=citizen.id,
                application_id=application_id,
                title=f"Processing Delayed — {step.step_name}",
                message=e.detail
            ))
            db.commit()
            return {"message": e.detail, "status": "ON_HOLD", "failed_step": step.step_name}

    # All steps done
    app.status = "COMPLETED"
    db.add(Notification(
        citizen_id=citizen.id,
        application_id=application_id,
        title=f"Application Completed — {app.service.name}",
        message=f"Your application {application_id} for {app.service.name} has been successfully processed."
    ))
    db.add(AuditLog(
        user_identifier=citizen.full_name,
        system="Sanyukt",
        action=f"Application Completed — {app.service.name}",
        application_id=application_id,
        status="SUCCESS"
    ))
    db.commit()
    return {"message": "Application processed successfully.", "status": "COMPLETED"}


# --- API Routes ---
class VerifyPropertyRequest(BaseModel):
    application_id: str
    citizen_id: str
    property_id: str


class WelfareCheckRequest(BaseModel):
    application_id: str
    citizen_id: str
    scheme_id: str


@router.post("/revenue/verify")
def revenue_verify(req: VerifyPropertyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rev_dept = db.query(Department).filter(Department.code == "REVENUE").first()
    connector = RevenueConnector(rev_dept, db)
    return connector.verify_property(req.application_id, req.citizen_id, req.property_id)


@router.post("/municipal/verify")
def municipal_verify(req: VerifyPropertyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mun_dept = db.query(Department).filter(Department.code == "MUNICIPAL").first()
    connector = MunicipalConnector(mun_dept, db)
    return connector.verify_property(req.application_id, req.property_id)


@router.post("/welfare/check")
def welfare_check(req: WelfareCheckRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wel_dept = db.query(Department).filter(Department.code == "WELFARE").first()
    connector = WelfareConnector(wel_dept, db)
    return connector.check_eligibility(req.application_id, req.citizen_id, req.scheme_id)


@router.post("/process/{application_id}")
def process(application_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return run_workflow(application_id, db)
