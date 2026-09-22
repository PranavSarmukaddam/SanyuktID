# Sanyukt ID — Prototype Launcher (PowerShell)
# Launches Sanyukt Central Backend and all 3 Simulated Department Portals

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   SANYUKT ID - MAHARASHTRA GOVERNMENT PROTOTYPE LAUNCHER" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not found in PATH. Please install Python 3.9+." -ForegroundColor Red
    Exit 1
}

Write-Host "[1/4] Starting Simulated Revenue Department (Port 8001)..." -ForegroundColor Green
$revenueProc = Start-Process python -ArgumentList "-m uvicorn main:app --port 8001 --host 0.0.0.0" -WorkingDirectory "$SCRIPT_DIR\department-portals\revenue-portal" -PassThru

Write-Host "[2/4] Starting Simulated Municipal Department (Port 8002)..." -ForegroundColor Green
$municipalProc = Start-Process python -ArgumentList "-m uvicorn main:app --port 8002 --host 0.0.0.0" -WorkingDirectory "$SCRIPT_DIR\department-portals\municipal-portal" -PassThru

Write-Host "[3/4] Starting Simulated Welfare Department (Port 8003)..." -ForegroundColor Green
$welfareProc = Start-Process python -ArgumentList "-m uvicorn main:app --port 8003 --host 0.0.0.0" -WorkingDirectory "$SCRIPT_DIR\department-portals\welfare-portal" -PassThru

Start-Sleep -Seconds 2

Write-Host "[4/4] Starting Sanyukt Central Backend & Portal (Port 8000)..." -ForegroundColor Green
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Sanyukt ID Portal is available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host " - Citizen Login: 9876543210 / citizen123" -ForegroundColor White
Write-Host " - Officer Login: OFFICER001 / officer123" -ForegroundColor White
Write-Host ""
Write-Host " Simulated Department APIs:" -ForegroundColor Cyan
Write-Host " - Revenue Dept:   http://localhost:8001/docs" -ForegroundColor White
Write-Host " - Municipal Dept: http://localhost:8002/docs" -ForegroundColor White
Write-Host " - Welfare Dept:   http://localhost:8003/docs" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Gray

# Run Central Backend in foreground
try {
    Set-Location "$SCRIPT_DIR\backend"
    python -m uvicorn main:app --port 8000 --host 0.0.0.0
}
finally {
    Write-Host "`nStopping simulated department services..." -ForegroundColor Yellow
    if ($revenueProc) { Stop-Process -Id $revenueProc.Id -ErrorAction SilentlyContinue }
    if ($municipalProc) { Stop-Process -Id $municipalProc.Id -ErrorAction SilentlyContinue }
    if ($welfareProc) { Stop-Process -Id $welfareProc.Id -ErrorAction SilentlyContinue }
    Write-Host "All services stopped." -ForegroundColor Green
}
