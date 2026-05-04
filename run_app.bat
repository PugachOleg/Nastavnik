@echo off
chcp 1251 >nul
title Family Mentor
cd /d "%~dp0"

echo Starting Family Mentor...

python -m pip install -r requirements.txt --quiet

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

streamlit run family_main.py --server.port 8501
pause