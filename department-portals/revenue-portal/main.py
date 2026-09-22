"""
Simulated Revenue Department Portal — Port 8001
This is a SIMULATED system for demonstration only.
Does not connect to real Maharashtra Government databases.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random, string

app = FastAPI(title="Revenue Department — Simulated Portal", description="SIMULATED SYSTEM — Prototype demonstration only.")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PROPERTY_DB = {
    "PROP-10291": {"owner_name": "Rajesh Kumar Sharma", "district": "Pune", "area_sqft": 1200, "survey_no": "SY-445/B", "type": "Residential", "tax_status": "Clear"},
    "PROP-10292": {"owner_name": "Sunita Patil", "district": "Mumbai", "area_sqft": 850, "survey_no": "SY-112/A", "type": "Commercial", "tax_status": "Clear"},
    "PROP-10293": {"owner_name": "Vikram Desai", "district": "Nagpur", "area_sqft": 2400, "survey_no": "SY-789/C", "type": "Agricultural", "tax_status": "Clear"},
}

CITIZEN_DB = {
    "MH-SYN-2026-000123": {"name": "Rajesh Kumar Sharma", "annual_income": 380000, "category": "OBC", "district": "Pune"},
}

cert_counter = [100]


class PropertyVerifyRequest(BaseModel):
    application_id: str
    citizen_id: str
    property_id: str


class IncomeVerifyRequest(BaseModel):
    application_id: str
    citizen_id: str


class CertificateRequest(BaseModel):
    application_id: str
    citizen_id: str
    cert_type: str


class StatusRequest(BaseModel):
    application_id: str


@app.post("/api/revenue/property/verify")
def verify_property(req: PropertyVerifyRequest):
    prop = PROPERTY_DB.get(req.property_id)
    if not prop:
        return {"status": "not_found", "property_id": req.property_id, "message": "Property record not found."}
    return {
        "status": "verified",
        "application_no": req.application_id,
        "property_id": req.property_id,
        "owner_name": prop["owner_name"],
        "district": prop["district"],
        "area_sqft": prop["area_sqft"],
        "survey_no": prop["survey_no"],
        "property_type": prop["type"],
        "tax_status": prop["tax_status"],
        "verified_at": datetime.utcnow().isoformat()
    }


@app.post("/api/revenue/income/verify")
def verify_income(req: IncomeVerifyRequest):
    citizen = CITIZEN_DB.get(req.citizen_id, {"name": "Citizen", "annual_income": 250000, "category": "General", "district": "Pune"})
    return {
        "status": "verified",
        "citizen_id": req.citizen_id,
        "citizen_name": citizen["name"],
        "annual_income": citizen["annual_income"],
        "income_category": "BPL" if citizen["annual_income"] < 100000 else "Middle",
        "category": citizen["category"],
        "verified_at": datetime.utcnow().isoformat()
    }


@app.post("/api/revenue/certificate/issue")
def issue_certificate(req: CertificateRequest):
    cert_counter[0] += 1
    cert_no = f"REV-CERT-{datetime.utcnow().year}-{cert_counter[0]:04d}"
    return {
        "status": "issued",
        "certificate_no": cert_no,
        "application_id": req.application_id,
        "citizen_id": req.citizen_id,
        "cert_type": req.cert_type,
        "issued_at": datetime.utcnow().isoformat(),
        "valid_until": "2027-09-22"
    }


@app.post("/api/revenue/status")
def get_status(req: StatusRequest):
    return {"application_id": req.application_id, "status": "processing", "department": "Revenue"}


@app.get("/health")
def health():
    return {"status": "ok", "system": "Revenue Department (Simulated)", "port": 8001}
