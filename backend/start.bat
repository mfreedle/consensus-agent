@echo off
REM Quick start script for Consensus Agent backend

echo Setting up Consensus Agent Backend...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Copying .env.example to .env...
    copy .env.example .env
    echo Please update .env with your API keys before proceeding!
    pause
)

REM Setup database
echo Setting up database...
python setup.py

REM Start development server
echo Starting development server...
python dev.py
