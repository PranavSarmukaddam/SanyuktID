"""
Sanyukt ID — Prototype Multi-Service Runner
Starts:
  1. Central Sanyukt Backend & Static Portal (Port 8000)
  2. Simulated Revenue Department (Port 8001)
  3. Simulated Municipal Department (Port 8002)
  4. Simulated Social Welfare Department (Port 8003)
"""
import subprocess
import sys
import os
import time
import signal

ROOT = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {
        "name": "Revenue Department (Simulated)",
        "port": 8001,
        "dir": os.path.join(ROOT, "department-portals", "revenue-portal"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--port", "8001", "--host", "0.0.0.0"],
    },
    {
        "name": "Municipal Department (Simulated)",
        "port": 8002,
        "dir": os.path.join(ROOT, "department-portals", "municipal-portal"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--port", "8002", "--host", "0.0.0.0"],
    },
    {
        "name": "Social Welfare Department (Simulated)",
        "port": 8003,
        "dir": os.path.join(ROOT, "department-portals", "welfare-portal"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--port", "8003", "--host", "0.0.0.0"],
    },
    {
        "name": "Sanyukt ID Central Platform",
        "port": 8000,
        "dir": os.path.join(ROOT, "backend"),
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"],
    },
]

processes = []

def cleanup(*args):
    print("\n[!] Shutting down all Sanyukt prototype services...")
    for p, name in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print("[+] All services stopped cleanly.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def main():
    print("=" * 64)
    print("    SANYUKT ID - MAHARASHTRA GOVERNMENT PROTOTYPE")
    print("=" * 64)
    print("Starting simulated department portals and central platform...\n")

    for svc in SERVICES:
        print(f"[*] Starting {svc['name']} on http://localhost:{svc['port']}...")
        p = subprocess.Popen(
            svc["cmd"],
            cwd=svc["dir"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        processes.append((p, svc["name"]))
        time.sleep(0.5)

    print("\n" + "=" * 64)
    print("   ALL SERVICES OPERATIONAL")
    print("=" * 64)
    print("  Central Portal:     http://localhost:8000")
    print("  Backend API Docs:   http://localhost:8000/docs")
    print("  Revenue Dept API:   http://localhost:8001/docs")
    print("  Municipal Dept API: http://localhost:8002/docs")
    print("  Welfare Dept API:   http://localhost:8003/docs")
    print("-" * 64)
    print("  Demo Citizen Login: 9876543210  / citizen123")
    print("  Demo Officer Login: OFFICER001  / officer123")
    print("=" * 64)
    print("\nPress Ctrl+C to stop all services.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
