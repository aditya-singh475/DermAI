@echo off
REM Comprehensive Setup and Start Script for Windows
REM This script performs complete setup and starts the application

setlocal enabledelayedexpansion

REM Get project directory
set PROJECT_DIR=%~dp0

echo.
echo ========================================
echo DermAI — Skin Health Screening
echo Complete Setup and Start Script
echo ========================================
echo.

REM Run Python setup script
echo Running Python setup script...
python setup.py

if errorlevel 1 (
    echo.
    echo ERROR: Setup script failed
    pause
    exit /b 1
)

REM Load environment from .env
echo.
echo Loading environment variables from .env...
for /f "delims== tokens=1,2" %%A in (.env) do (
    if not "%%A"=="" if not "%%A:~0,1%%"=="#" (
        set %%A=%%B
    )
)

echo ========================================
echo Starting Application
echo ========================================
echo.

REM Start backend server
echo Starting Backend Server on port 8000...
start "DermAI Backend" cmd /k ^
    cd /d "%PROJECT_DIR%backend" && ^
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

timeout /t 3

REM Start frontend server
echo Starting Frontend Dev Server on port 5173...
start "DermAI Frontend" cmd /k ^
    cd /d "%PROJECT_DIR%frontend" && ^
    npm run dev

echo.
echo ========================================
echo Application Started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close the terminal windows when done.
echo.

pause
