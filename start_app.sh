#!/bin/bash

# Function to kill all child processes on exit
cleanup() {
    echo "Shutting down servers..."
    # Kill all child processes in the current process group
    kill $(jobs -p) 2>/dev/null
}

# Trap SIGINT (Ctrl+C) and EXIT
trap cleanup SIGINT EXIT

echo "Starting AI Data Chatbot..."

# check if we are in the root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory."
    exit 1
fi

# Check and install Root dependencies (for MCP Client)
if [ ! -d "node_modules" ]; then
    echo "Root node_modules not found. Installing dependencies..."
    npm install
fi

# Check and install Frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "Frontend node_modules not found. Installing dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -d "backend/.venv" ]; then
    echo "Activating backend virtual environment..."
    source backend/.venv/bin/activate
else
    echo "Warning: No .venv found. Assuming Python environment is already set up."
fi

# Start Backend
echo "Starting Backend Server (FastAPI)..."
# We run uvicorn as a module from the root so that imports like 'backend.app' work correctly
python -m uvicorn backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start Frontend
echo "Starting Frontend Server (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
