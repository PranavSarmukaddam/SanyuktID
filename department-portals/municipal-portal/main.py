"""
Simulated Municipal Department Portal — Port 8002
This is a SIMULATED system for demonstration only.
Does not connect to real Maharashtra Government databases.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Municipal Department — Simulated Portal", description="SIMULATED SYSTEM — Prototype demonstration only.")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PROPERTY_DB = {
    "PROP-10291": {"property_owner": "Rajesh Kumar Sharma", "municipal_zone": "Zone 4", "tax_status": "Clear", "usage": "Residential", "water_connection": "Active"},
    "PROP-10292": {"property_owner": "Sunita Patil", "municipal_zone": "Zone 2", "tax_status": "Clear", "usage": "Commercial", "water_connection": "Active"},
    "PROP-10293": {"property_owner": "Vikram Desai", "municipal_zone": "Zone 7", "tax_status": "Pending", "usage": "Agricultural", "water_connection": "None"},
}

approval_counter = [200]


class PropertyVerifyRequest(BaseModel):
    application_id: str
    property_id: str


class SiteVerifyRequest(BaseModel):
    application_id: str
    property_id: str


class ApproveRequest(BaseModel):
    application_id: str


@app.post("/api/municipal/property/verify")
def verify_property(req: PropertyVerifyRequest):
    prop = PROPERTY_DB.get(req.property_id)
    if not prop:
        return {"status": "not_found", "property_id": req.property_id, "message": "Property not found in municipal records."}
    return {
        "status": "verified",
        "application_id": req.application_id,
        "property_id": req.property_id,
        "property_owner": prop["property_owner"],
        "municipal_zone": prop["municipal_zone"],
        "tax_status": prop["tax_status"],
        "property_usage": prop["usage"],
        "water_connection": prop["water_connection"],
        "verified_at": datetime.utcnow().isoformat()
    }


@app.post("/api/municipal/site/verify")
def verify_site(req: SiteVerifyRequest):
    prop = PROPERTY_DB.get(req.property_id, {"municipal_zone": "Zone 4", "tax_status": "Clear"})
    return {
        "status": "verified",
        "application_id": req.application_id,
        "property_id": req.property_id,
        "site_inspection": "Completed",
        "municipal_zone": prop["municipal_zone"],
        "building_regulation_clearance": "Granted",
        "verified_at": datetime.utcnow().isoformat()
    }


@app.post("/api/municipal/approve")
def approve(req: ApproveRequest):
    approval_counter[0] += 1
    approval_no = f"MUN-APPR-{datetime.utcnow().year}-{approval_counter[0]:04d}"
    return {
        "status": "approved",
        "approval_no": approval_no,
        "application_id": req.application_id,
        "approved_at": datetime.utcnow().isoformat(),
        "valid_until": "2027-09-22"
    }


@app.get("/health")
def health():
    return {"status": "ok", "system": "Municipal Department (Simulated)", "port": 8002}
