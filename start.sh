#!/bin/bash
# Skin Health Detection System - Startup Script for Linux/Mac

# Set environment variables
export SECRET_KEY=umxsYd1SclM8sc47uXQ6tWws8ef_AX4a5aTHxMVniR0

echo "========================================"
echo "Starting Backend Server..."
echo "========================================"
cd "$(dirname "$0")/backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

echo ""
echo "========================================"
echo "Starting Frontend Dev Server..."
echo "========================================"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Startup Complete!"
echo "========================================"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop servers"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
