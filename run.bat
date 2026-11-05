@echo off
echo ========================================================
echo       Starting Affan Accounting OS
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Creating .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install fastapi "uvicorn[standard]" sqlalchemy pydantic python-multipart
)

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Affan Backend" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Vite React Frontend on http://localhost:5173 ...
cd frontend
start "Affan Frontend" cmd /k "npm.cmd run dev"

echo.
echo ========================================================
echo Affan Accounting OS is running!
echo App URL:     http://localhost:5173
echo Backend API: http://127.0.0.1:8000/docs
echo ========================================================
echo.
timeout /t 3 >nul
start http://localhost:5173

