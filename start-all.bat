@echo off
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn api.app:app --reload"
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 5
start http://localhost:5173