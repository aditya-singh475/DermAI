#!/bin/bash
# Comprehensive Setup and Start Script for Linux/Mac
# This script performs complete setup and starts the application

set -e  # Exit on error

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Main setup
main() {
    print_header "Skin Health Detection System - Complete Setup"
    
    # Run Python setup script
    print_header "Running Python Setup Script"
    python3 setup.py
    
    if [ $? -ne 0 ]; then
        print_error "Setup script failed"
        exit 1
    fi
    
    print_header "Starting Application"
    
    # Load environment
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        print_success "Loaded environment variables from .env"
    fi
    
    # Start backend in background
    print_info "Starting backend server on port 8000..."
    cd "$PROJECT_DIR/backend"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    print_success "Backend started (PID: $BACKEND_PID)"
    
    sleep 2
    
    # Start frontend
    print_info "Starting frontend dev server on port 5173..."
    cd "$PROJECT_DIR/frontend"
    npm run dev &
    FRONTEND_PID=$!
    print_success "Frontend started (PID: $FRONTEND_PID)"
    
    echo ""
    print_header "Application Running!"
    echo ""
    echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
    echo -e "${GREEN}Frontend:${NC} http://localhost:5173"
    echo ""
    echo "Press Ctrl+C to stop servers"
    echo ""
    
    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Cleanup function
cleanup() {
    print_info "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    print_success "Servers stopped"
}

# Trap Ctrl+C
trap cleanup INT TERM

# Run main
main
