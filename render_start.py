"""
render_start.py - Single-process launcher for Render.com deployment.
Starts all 4 Sanyukt servers inside one dyno:
  Revenue dept    -> localhost:8001 (internal only)
  Municipal dept  -> localhost:8002 (internal only)
  Welfare dept    -> localhost:8003 (internal only)
  Central backend -> 0.0.0.0:PORT  (public, Render exposes this)
No functionality is changed.
"""
import os, sys, threading, time

ROOT = os.path.dirname(os.path.abspath(__file__))

def run_dept(portal_dir, port, name):
    import subprocess
    print(f"[dept] Starting {name} on :{port}")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=portal_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

DEPT_PORTALS = [
    ("revenue-portal",   8001, "Revenue Dept"),
    ("municipal-portal", 8002, "Municipal Dept"),
    ("welfare-portal",   8003, "Welfare Dept"),
]

for folder, port, name in DEPT_PORTALS:
    portal_dir = os.path.join(ROOT, "department-portals", folder)
    t = threading.Thread(target=run_dept, args=(portal_dir, port, name), daemon=True)
    t.start()

time.sleep(2)

import uvicorn
PORT = int(os.environ.get("PORT", 8000))
os.chdir(os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "backend"))
print(f"[main] Starting Sanyukt Central on :{PORT}")
uvicorn.run("main:app", host="0.0.0.0", port=PORT, log_level="info")
