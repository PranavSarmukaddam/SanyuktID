# Sanyukt ID — Maharashtra Unified Digital Service Platform

> **PROTOTYPE NOTICE:** This is a working prototype developed for demonstrating unified digital identity and cross-department interoperability for the Government of Maharashtra. All department endpoints, citizen data, and certificates are simulated for demonstration purposes.

---

## 🏛 Overview

**Sanyukt ID** solves the challenge of siloed government departmental databases by providing:
1. **Unified Citizen Identity (`MH-SYN-XXXX-XXXXXX`)**: Single identity card linking citizen profile, contact info, and district data.
2. **Interoperability Engine**: Seamless API orchestration between departments (Revenue, Municipal Corporations, Social Welfare).
3. **Citizen Consent Management**: Explicit consent architecture giving citizens control over which departments access their data.
4. **End-to-End Application Tracking**: Unified status, step-by-step progress timeline, and notification center.
5. **Officer Administration & Observability**: Real-time stats, failure simulation mode (to test resilience and retry mechanisms), and complete audit/API logs.
6. **Authentic Government Portal UI**: Minimalist, realistic Maharashtra State Government aesthetic (Navy Blue, Maharashtra Gold, Crisp Tables, Accessible Forms).

---

## ⚙️ Architecture

```
                 ┌─────────────────────────────────────────┐
                 │       Citizen & Officer Web Portal       │
                 │      (Plain HTML5 / Vanilla CSS & JS)   │
                 └────────────────────┬────────────────────┘
                                      │ HTTP / JSON
                                      ▼
                 ┌─────────────────────────────────────────┐
                 │        Sanyukt Central Platform         │
                 │        (FastAPI / SQLite / JWT)         │
                 │                Port: 8000               │
                 └──────┬─────────────┬─────────────┬──────┘
                        │             │             │
        REST API Calls  │             │             │
     with Normalization │             │             │
                        ▼             ▼             ▼
       ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
       │   Revenue Dept   │  │  Municipal Dept  │  │   Welfare Dept   │
       │ (Simulated API)  │  │ (Simulated API)  │  │ (Simulated API)  │
       │    Port: 8001    │  │    Port: 8002    │  │    Port: 8003    │
       └──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.9 or higher
- Windows PowerShell or Bash terminal

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Start All Services

You can launch all 4 services with either:

#### Option A: Python Runner (Recommended)
```powershell
python start_all.py
```

#### Option B: PowerShell Script
```powershell
.\run.ps1
```

---

## 🔑 Demo Credentials

| Role | Username / ID | Password | Access Details |
|---|---|---|---|
| **Citizen** | `9876543210` | `citizen123` | Rajesh Kumar Sharma (Pune) — Access to citizen services, digital ID card, application submission & tracking, consent management, notifications |
| **Officer** | `OFFICER001` | `officer123` | Priya Mehta (Deputy Collector) — Access to officer dashboard, cross-department applications, failure simulation switch, audit logs |

---

## 🌐 Port & Endpoint Reference

| Service | Port | Base URL | Swagger Docs |
|---|---|---|---|
| **Sanyukt Central Portal & Backend** | `8000` | http://localhost:8000 | http://localhost:8000/docs |
| **Revenue Department API** | `8001` | http://localhost:8001 | http://localhost:8001/docs |
| **Municipal Department API** | `8002` | http://localhost:8002 | http://localhost:8002/docs |
| **Social Welfare Department API** | `8003` | http://localhost:8003 | http://localhost:8003/docs |

---

## 📄 Key Pages & Workflows

1. **Home (`/index.html`)**: Overview of the Sanyukt ID system, participating departments, features, and quick login links.
2. **Citizen Dashboard (`/dashboard.html`)**: Digital Sanyukt ID card with barcode/emblem, quick application stats, and recent activities.
3. **Services Listing (`/services.html`)**: Grouped services across Revenue (Property Transfer, 7/12 Extract, Income Certificate, Domicile), Municipal (Building Permission, Water Connection, Birth Certificate), and Social Welfare (Scholarship, Welfare Scheme, Financial Assistance).
4. **Service Application Form (`/apply.html?service=...`)**: 3-step application workflow:
   - Step 1: Pre-filled Identity verification via Sanyukt ID.
   - Step 2: Granular data-sharing consent.
   - Step 3: Service-specific form submission.
5. **Application Details (`/application-detail.html?id=...`)**: Live timeline showing multi-department verification steps, error traces, and processing triggers.
6. **Officer Dashboard (`/officer-dashboard.html`)**: Application volume stats, department API health metrics, and failure simulation controls.
7. **Audit & Trace Logs (`/audit-logs.html`)**: Immutable record of all system events and raw inter-departmental HTTP API calls.
8. **Consent Management (`/consent.html`)**: View granted data authorizations and revoke department access anytime.
