@echo off
REM Start Backend Server Script for Windows

echo Loading environment variables from .env file...
for /f "delims== tokens=1,2" %%A in (.env) do (
    if not "%%A"=="" if not "%%A:~0,1%%"=="#" (
        set %%A=%%B
    )
)

echo ========================================
echo Starting Backend Server
echo ========================================
echo Port: 8000
echo Reload: Enabled
echo.

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
