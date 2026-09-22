import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import create_tables, seed_data
from routers import auth, applications, consent, interoperability, audit, departments, notifications, officers, services

app = FastAPI(
    title="Sanyukt ID — Interoperability Platform",
    description="Maharashtra Government-style unified digital identity and interoperability platform. PROTOTYPE — Simulated department systems for demonstration only.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(consent.router, prefix="/api/consent", tags=["Consent"])
app.include_router(interoperability.router, prefix="/api/interoperability", tags=["Interoperability"])
app.include_router(audit.router, prefix="/api/audit-logs", tags=["Audit"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(officers.router, prefix="/api/officer", tags=["Officer"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

    @app.get("/")
    def home():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{page}.html")
    def serve_page(page: str):
        file_path = os.path.join(frontend_path, f"{page}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/favicon.ico")
    def favicon():
        fav_path = os.path.join(frontend_path, "static", "img", "sanyukt.png")
        if os.path.exists(fav_path):
            return FileResponse(fav_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.on_event("startup")
def startup():
    create_tables()
    seed_data()
    print("Sanyukt ID backend started. Docs at http://localhost:8000/docs")


@app.get("/health")
def health():
    return {"status": "ok", "service": "Sanyukt ID Backend"}
