#!/bin/bash

# Application Start Script (TEMPLATE)
# This script starts your application services (backend, frontend, etc.)
#
# CUSTOMIZATION REQUIRED:
# 1. Update port numbers for your application
# 2. Update directory paths (BACKEND_DIR, FRONTEND_DIR)
# 3. Replace backend/frontend start commands
# 4. Adjust .env file checks or remove if not needed
# 5. Customize service names and URLs
#
# See store/CUSTOMIZATION_GUIDE.md for examples for different tech stacks

# TODO: Customize these configuration values
SERVER_PORT=8000          # Backend server port
CLIENT_PORT=5173          # Frontend client port (if applicable)
BACKEND_DIR="backend"     # Path to backend directory (relative to project root)
FRONTEND_DIR="frontend"   # Path to frontend directory (relative to project root, or empty if no frontend)
ENV_FILE_PATH=""          # Path to required .env file (e.g., "backend/.env"), or empty to skip check

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Application...${NC}"

# Function to kill process on port
kill_port() {
    local port=$1
    local process_name=$2

    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)

    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Found $process_name running on port $port (PID: $pid). Killing it...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        echo -e "${GREEN}$process_name on port $port has been terminated.${NC}"
    fi
}

# Kill any existing processes on our ports
kill_port $SERVER_PORT "backend server"
if [ ! -z "$FRONTEND_DIR" ]; then
    kill_port $CLIENT_PORT "frontend server"
fi

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Optional: Check if .env file exists (customize or remove this section)
if [ ! -z "$ENV_FILE_PATH" ] && [ ! -f "$PROJECT_ROOT/$ENV_FILE_PATH" ]; then
    echo -e "${RED}Warning: No .env file found at $ENV_FILE_PATH${NC}"
    echo "You may need to:"
    echo "  1. Create an .env file from .env.sample"
    echo "  2. Add required configuration values"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to cancel..."
    read
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"

    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null

    # Wait for processes to terminate
    wait

    echo -e "${GREEN}Services stopped successfully.${NC}"
    exit 0
}

# Trap EXIT, INT, and TERM signals
trap cleanup EXIT INT TERM

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
cd "$PROJECT_ROOT/$BACKEND_DIR"

# TODO: Replace this command with your backend start command
# Examples:
#   Python/FastAPI: uvicorn main:app --reload --port $SERVER_PORT
#   Python/Flask: flask run --port $SERVER_PORT
#   Node.js: npm start
#   Go: go run main.go
#   Rust: cargo run
#   .NET: dotnet run
uv run python server.py &  # <-- CUSTOMIZE THIS LINE
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start!${NC}"
    exit 1
fi

# Start frontend (if applicable - remove this section if you don't have a frontend)
if [ ! -z "$FRONTEND_DIR" ]; then
    echo -e "${GREEN}Starting frontend server...${NC}"
    cd "$PROJECT_ROOT/$FRONTEND_DIR"

    # TODO: Replace this command with your frontend start command
    # Examples:
    #   React: npm start
    #   Vue: npm run dev
    #   Angular: ng serve
    #   Vite: npm run dev
    #   Next.js: npm run dev
    npm run dev &  # <-- CUSTOMIZE THIS LINE
    FRONTEND_PID=$!

    # Wait for frontend to start
    sleep 3

    # Check if frontend is running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}Frontend failed to start!${NC}"
        exit 1
    fi
fi

# Success messages
echo -e "${GREEN}✓ Services started successfully!${NC}"
if [ ! -z "$FRONTEND_DIR" ]; then
    echo -e "${BLUE}Frontend: http://localhost:$CLIENT_PORT${NC}"
fi
echo -e "${BLUE}Backend:  http://localhost:$SERVER_PORT${NC}"
# Uncomment and customize if you have API docs
# echo -e "${BLUE}API Docs: http://localhost:$SERVER_PORT/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user to press Ctrl+C
wait
