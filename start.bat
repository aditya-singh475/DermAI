@echo off
REM Skin Health Detection System - Startup Script for Windows
REM This script sets up the environment and starts the application

setlocal enabledelayedexpansion

REM Set environment variables
set SECRET_KEY=umxsYd1SclM8sc47uXQ6tWws8ef_AX4a5aTHxMVniR0

REM Add current directory to Python path
set PYTHONPATH=%cd%;!PYTHONPATH!

echo ========================================
echo Starting Backend Server...
echo ========================================
cd backend
start "Backend Server" cmd /k uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

timeout /t 3

echo.
echo ========================================
echo Starting Frontend Dev Server...
echo ========================================
cd ..\frontend
start "Frontend Dev Server" cmd /k npm run dev

echo.
echo ========================================
echo Startup Complete!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
