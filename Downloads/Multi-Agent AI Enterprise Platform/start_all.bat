@echo off
cd /d "%~dp0"

echo Launching backend and frontend in two separate windows...
start "AI Agent Backend (port 8000)" cmd /k start_backend.bat
timeout /t 5 /nobreak >nul
start "AI Agent Frontend (port 5173)" cmd /k start_frontend.bat

echo.
echo Two windows should now be open:
echo   - Backend window  -^> must say "Application startup complete"
echo   - Frontend window -^> must say "Local: http://localhost:5173"
echo Then open http://localhost:5173 in your browser and click "Launch AI Router".
pause
