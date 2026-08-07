@echo off
cd /d "%~dp0\frontend"

echo Installing frontend dependencies (first run only)...
call npm install

echo Starting frontend on http://localhost:5173 ...
call npm run dev

pause
