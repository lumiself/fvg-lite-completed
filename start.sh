#!/bin/bash

# FVG Silver Bullet Lite - Linux/Mac Startup Script
echo "========================================"
echo "FVG Silver Bullet Lite - Linux/Mac Startup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 for Python 3"
    exit 1
fi

# Navigate to script directory
cd "$(dirname "$0")"

# Install Python dependencies if not already installed
echo "Checking Python dependencies..."
cd backend
python3 -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Python dependencies..."
    pip3 install -r ../requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Start the WebSocket server
echo "Starting WebSocket server..."
echo "Server will run on: ws://localhost:8765"
echo ""
echo "To access the application:"
echo "1. Open frontend/index.html in your browser"
echo "2. Or use frontend/test-websocket.html for testing"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
python3 websocket_server.py
