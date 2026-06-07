@echo off
REM Start Frontend Server Script for Windows

echo ========================================
echo Starting Frontend Dev Server
echo ========================================
echo Port: 5173
echo.

cd frontend
call npm run dev

pause
