Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      Starting Affan Accounting OS" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\pip.exe install fastapi "uvicorn[standard]" sqlalchemy pydantic python-multipart
}

Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[2/2] Starting Vite React Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm.cmd run dev"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "WealthPulse running!" -ForegroundColor Green
Write-Host "Frontend:    http://localhost:5173"
Write-Host "Swagger API: http://127.0.0.1:8000/docs"

