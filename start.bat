@echo off
:: ──────────────────────────────────────────────────────────
:: Partner Scorecard — Windows Launcher
:: Double-click this file to start the app.
:: ──────────────────────────────────────────────────────────

cd /d "%~dp0"

echo.
echo   Partner Scorecard
echo   -----------------
echo.

:: ── Check for Python 3 ──
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   Python 3 is required but not installed.
    echo.
    echo   Install it from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo   Using %%i

:: ── Create virtual environment if needed ──
if not exist ".venv" (
    echo   Setting up (first run only^)...
    python -m venv .venv
)

:: ── Activate and install dependencies ──
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul

echo   Starting app — your browser will open shortly...
echo.

:: ── Launch ──
streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
