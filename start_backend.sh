#!/bin/bash
# Start Backend Server Script for Linux/Mac

echo "Loading environment variables..."
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "========================================"
echo "Starting Backend Server"
echo "========================================"
echo "Port: 8000"
echo "Reload: Enabled"
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
