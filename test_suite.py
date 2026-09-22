import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from main import app
from database import create_tables, seed_data

create_tables()
seed_data()

client = TestClient(app)

print("[1] Testing Citizen Login...")
c_login = client.post("/api/auth/login", json={"username": "9876543210", "password": "citizen123"})
assert c_login.status_code == 200, f"Citizen login failed: {c_login.text}"
c_token = c_login.json()["access_token"]
c_headers = {"Authorization": f"Bearer {c_token}"}
print(f"    Success: {c_login.json()['citizen_name']} ({c_login.json()['sanyukt_id']})")

print("[2] Testing Officer Login...")
o_login = client.post("/api/auth/login", json={"username": "OFFICER001", "password": "officer123"})
assert o_login.status_code == 200, f"Officer login failed: {o_login.text}"
o_token = o_login.json()["access_token"]
o_headers = {"Authorization": f"Bearer {o_token}"}
print(f"    Success: {o_login.json()['officer_name']} ({o_login.json()['department']})")

print("[3] Testing Services Listing...")
services = client.get("/api/services").json()
print(f"    Found {len(services)} services across departments.")
assert len(services) >= 10

print("[4] Testing Application Submission...")
app_res = client.post(
    "/api/applications",
    json={"service_code": "PROP_TRANSFER", "form_data": {"property_id": "PROP-10291", "buyer_name": "Test User"}},
    headers=c_headers,
)
assert app_res.status_code == 200
app_id = app_res.json()["application_id"]
print(f"    Application created: {app_id} (Status: {app_res.json()['status']})")

print("[5] Testing Application Details Retrieval...")
detail = client.get(f"/api/applications/{app_id}", headers=c_headers).json()
assert detail["application_id"] == app_id
print(f"    Fetched details with {len(detail['steps'])} workflow steps.")

print("[6] Testing Citizen Consent Recording...")
consent = client.post(
    "/api/consent",
    json={"application_id": app_id, "department_code": "REVENUE", "data_types": "identity,property", "granted": True},
    headers=c_headers,
).json()
print(f"    Consent: {consent['message']}")

print("[7] Testing Officer Failure Simulation Toggle...")
fail_on = client.post(
    "/api/departments/failure-mode",
    json={"department_code": "REVENUE", "failure_mode": True},
    headers=o_headers,
).json()
print(f"    {fail_on['message']}")

print("[8] Testing Workflow Execution Under Failure Mode (Graceful Degradation)...")
wf_result = client.post(f"/api/applications/{app_id}/process", headers=c_headers).json()
print(f"    Workflow response: {wf_result['status']} — {wf_result['message']}")
assert wf_result["status"] == "ON_HOLD"

# Verify application is ON_HOLD in DB
app_check = client.get(f"/api/applications/{app_id}", headers=c_headers).json()
assert app_check["status"] == "ON_HOLD"
print("    Verified: Application placed on ON_HOLD state as specified.")

print("[9] Restoring Failure Mode...")
fail_off = client.post(
    "/api/departments/failure-mode",
    json={"department_code": "REVENUE", "failure_mode": False},
    headers=o_headers,
).json()
print(f"    {fail_off['message']}")

print("[10] Testing Officer Stats & Audit Logs...")
stats = client.get("/api/officer/stats", headers=o_headers).json()
print(f"    Officer Stats: Total={stats['total']}, OnHold={stats['on_hold']}, Completed={stats['completed']}")

audit = client.get(f"/api/audit-logs?application_id={app_id}", headers=o_headers).json()
print(f"    Audit trail count for {app_id}: {len(audit)}")
assert len(audit) >= 1

api_logs = client.get("/api/audit-logs/api-logs", headers=o_headers).json()
print(f"    Total API logs recorded: {len(api_logs)}")

print("\n" + "=" * 50)
print("  ALL 10 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
print("=" * 50)
