"""
Simulated Social Welfare Department Portal — Port 8003
This is a SIMULATED system for demonstration only.
Does not connect to real Maharashtra Government databases.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Social Welfare Department — Simulated Portal", description="SIMULATED SYSTEM — Prototype demonstration only.")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SCHEMES = {
    "SCHOLAR-01": {"name": "Education Assistance Scheme", "income_limit": 500000, "categories": ["OBC", "SC", "ST", "General"]},
    "WELFARE-01": {"name": "General Welfare Scheme", "income_limit": 250000, "categories": ["OBC", "SC", "ST"]},
    "FIN-01": {"name": "Financial Assistance Programme", "income_limit": 150000, "categories": ["OBC", "SC", "ST"]},
}

CITIZEN_DB = {
    "MH-SYN-2026-000123": {"name": "Rajesh Kumar Sharma", "annual_income": 380000, "category": "OBC"},
}


class EligibilityRequest(BaseModel):
    application_id: str
    citizen_id: str
    scheme_id: str


@app.post("/api/welfare/eligibility/check")
def check_eligibility(req: EligibilityRequest):
    scheme = SCHEMES.get(req.scheme_id, SCHEMES["SCHOLAR-01"])
    citizen = CITIZEN_DB.get(req.citizen_id, {"name": "Citizen", "annual_income": 200000, "category": "OBC"})

    eligible = citizen["annual_income"] <= scheme["income_limit"] and citizen["category"] in scheme["categories"]

    return {
        "status": "eligible" if eligible else "not_eligible",
        "application_id": req.application_id,
        "citizen_id": req.citizen_id,
        "scheme": scheme["name"],
        "scheme_id": req.scheme_id,
        "income_limit": scheme["income_limit"],
        "citizen_income": citizen["annual_income"],
        "category": citizen["category"],
        "verification": "completed",
        "verified_at": datetime.utcnow().isoformat()
    }


@app.get("/health")
def health():
    return {"status": "ok", "system": "Social Welfare Department (Simulated)", "port": 8003}
