import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, Application

client = TestClient(app)

print("[*] Testing Full Multi-Department Workflow Execution...")

# 1. Citizen Login
c_login = client.post("/api/auth/login", json={"username": "9876543210", "password": "citizen123"}).json()
c_headers = {"Authorization": f"Bearer {c_login['access_token']}"}

# 2. Submit new Property Transfer Application
app_res = client.post(
    "/api/applications",
    json={"service_code": "PROP_TRANSFER", "form_data": {"property_id": "PROP-10291", "buyer_name": "Deepak Shinde"}},
    headers=c_headers,
).json()
app_id = app_res["application_id"]
print(f"    Application Created: {app_id}")

# 3. Simulate responses from Revenue and Municipal APIs
def mock_httpx_post(url, json=None, timeout=None):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    if "/api/revenue/property/verify" in url:
        mock_resp.json.return_value = {
            "status": "verified",
            "property_id": json.get("property_id"),
            "owner_name": "Rajesh Kumar Sharma",
            "district": "Pune",
            "tax_status": "Clear",
        }
    elif "/api/municipal/property/verify" in url:
        mock_resp.json.return_value = {
            "status": "verified",
            "property_id": json.get("property_id"),
            "municipal_zone": "Zone 4",
            "water_connection": "Active",
            "tax_status": "Clear",
        }
    elif "/api/revenue/certificate/issue" in url:
        mock_resp.json.return_value = {
            "status": "issued",
            "certificate_no": "REV-CERT-2026-9999",
            "valid_until": "2027-09-22",
        }
    else:
        mock_resp.json.return_value = {"status": "ok"}
    return mock_resp

with patch("routers.interoperability.httpx.post", side_effect=mock_httpx_post):
    proc = client.post(f"/api/applications/{app_id}/process", headers=c_headers).json()
    print(f"    Workflow Engine Output: {proc['status']} — {proc['message']}")
    assert proc["status"] == "COMPLETED"

# 4. Verify Application State
detail = client.get(f"/api/applications/{app_id}", headers=c_headers).json()
assert detail["status"] == "COMPLETED"
print(f"    Application {app_id} Status: {detail['status']}")

# Check that all 5 steps are marked COMPLETED
for s in detail["steps"]:
    print(f"      Step {s['step_number']} [{s['department']}]: {s['step_name']} -> {s['status']}")
    assert s["status"] == "COMPLETED"

# 5. Check Citizen Notifications
notifs = client.get("/api/notifications", headers=c_headers).json()
app_notifs = [n for n in notifs if n.get("application_id") == app_id]
print(f"    Notifications received for {app_id}: {len(app_notifs)}")
assert len(app_notifs) >= 1

print("\n[SUCCESS] FULL END-TO-END WORKFLOW EXECUTION VERIFIED SUCCESSFULLY!")
