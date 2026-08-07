@echo off
cd /d "%~dp0"

if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

echo [2/3] Activating venv and installing ALL dependencies (this can take a few minutes the first time)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements-all.txt

echo [3/3] Starting backend on http://127.0.0.1:8000 ...
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
