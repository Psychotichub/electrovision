#!/bin/bash

# ElectroVision AI - Startup Script
# This script starts the complete ElectroVision AI system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[ElectroVision AI]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        print_warning "Port $1 is in use. Killing existing process..."
        lsof -ti:$1 | xargs kill -9
        sleep 2
    fi
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION detected"
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION detected"
    
    # Check npm
    if ! command_exists npm; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION detected"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Install Python dependencies
    if [ ! -f "venv/.deps_installed" ]; then
        print_status "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        touch venv/.deps_installed
        print_success "Python dependencies installed"
    else
        print_success "Python dependencies already installed"
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Install dependencies if not already installed
    if [ ! -d "node_modules" ]; then
        print_status "Installing backend dependencies..."
        npm install
        print_success "Backend dependencies installed"
    else
        print_success "Backend dependencies already installed"
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
PORT=3000
NODE_ENV=development
UPLOAD_DIR=uploads
PYTHON_CMD=python3
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=.pdf,.dwg,.dxf
CORS_ORIGIN=http://localhost:3001
LOG_LEVEL=info
EOF
        print_success ".env file created"
    fi
    
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies if not already installed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_success "Frontend dependencies already installed"
    fi
    
    cd ..
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "backend/uploads"
        "data/raw"
        "data/processed"
        "logs"
        "ai_model/dataset/images/train"
        "ai_model/dataset/images/val"
        "ai_model/dataset/labels/train"
        "ai_model/dataset/labels/val"
        "ai_model/runs"
        "models"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    print_success "Directories created"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    # Kill any existing process on port 3000
    kill_port 3000
    
    cd backend
    
    # Start backend in background
    nohup npm start > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Check if backend is running
    if check_port 3000; then
        print_success "Backend server started on port 3000 (PID: $BACKEND_PID)"
    else
        print_error "Failed to start backend server"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    # Kill any existing process on port 3001
    kill_port 3001
    
    cd frontend
    
    # Start frontend in background
    nohup npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    # Check if frontend is running
    if check_port 3001; then
        print_success "Frontend server started on port 3001 (PID: $FRONTEND_PID)"
    else
        print_error "Failed to start frontend server"
        exit 1
    fi
}

# Function to open browser
open_browser() {
    print_status "Opening browser..."
    
    if command_exists xdg-open; then
        xdg-open http://localhost:3001
    elif command_exists open; then
        open http://localhost:3001
    elif command_exists start; then
        start http://localhost:3001
    else
        print_warning "Could not open browser automatically"
        print_status "Please open http://localhost:3001 in your browser"
    fi
}

# Function to show status
show_status() {
    echo
    print_status "ElectroVision AI System Status"
    echo "=================================="
    
    if check_port 3000; then
        print_success "Backend: Running on http://localhost:3000"
    else
        print_error "Backend: Not running"
    fi
    
    if check_port 3001; then
        print_success "Frontend: Running on http://localhost:3001"
    else
        print_error "Frontend: Not running"
    fi
    
    echo
    print_status "Log files:"
    echo "  Backend:  logs/backend.log"
    echo "  Frontend: logs/frontend.log"
    
    echo
    print_status "To stop the system, run: ./run.sh stop"
}

# Function to stop all services
stop_services() {
    print_status "Stopping ElectroVision AI services..."
    
    # Stop backend
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend stopped"
        fi
        rm -f logs/backend.pid
    fi
    
    # Stop frontend
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend stopped"
        fi
        rm -f logs/frontend.pid
    fi
    
    # Kill any remaining processes on our ports
    kill_port 3000
    kill_port 3001
    
    print_success "All services stopped"
}

# Function to show help
show_help() {
    echo "ElectroVision AI - Startup Script"
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Start the complete system (default)"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  status    Show system status"
    echo "  setup     Setup environment only"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0              # Start the system"
    echo "  $0 start        # Start the system"
    echo "  $0 stop         # Stop all services"
    echo "  $0 restart      # Restart all services"
    echo "  $0 status       # Show current status"
}

# Main function
main() {
    # Create logs directory
    mkdir -p logs
    
    case "${1:-start}" in
        "start")
            echo "⚡ ElectroVision AI - Starting System"
            echo "====================================="
            setup_environment
            create_directories
            setup_backend
            setup_frontend
            start_backend
            start_frontend
            show_status
            open_browser
            echo
            print_success "ElectroVision AI is now running!"
            print_status "Access the application at: http://localhost:3001"
            ;;
        "stop")
            echo "⚡ ElectroVision AI - Stopping System"
            echo "===================================="
            stop_services
            ;;
        "restart")
            echo "⚡ ElectroVision AI - Restarting System"
            echo "======================================"
            stop_services
            sleep 2
            start_backend
            start_frontend
            show_status
            ;;
        "status")
            show_status
            ;;
        "setup")
            echo "⚡ ElectroVision AI - Environment Setup"
            echo "======================================"
            setup_environment
            create_directories
            setup_backend
            setup_frontend
            print_success "Environment setup complete!"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Trap to cleanup on exit
trap 'echo; print_status "Shutting down..."; stop_services; exit 0' INT TERM

# Run main function
main "$@" 