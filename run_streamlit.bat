@echo off
title SBU/PO Dashboard - Streamlit
echo Starting SBU/PO Dashboard (Streamlit Version)...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install Streamlit requirements if needed
echo Installing/updating requirements...
pip install -r requirements_streamlit.txt --quiet

REM Check if sbu_app.py exists
if not exist "sbu_app.py" (
    echo ERROR: sbu_app.py not found
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)

REM Launch Streamlit application
echo.
echo Launching Streamlit application...
echo Your browser should open automatically
echo.
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
streamlit run sbu_app.py

pause
