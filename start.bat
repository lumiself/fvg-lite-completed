@echo off
echo ========================================
echo FVG Silver Bullet Lite - Windows Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Install Python dependencies if not already installed
echo Checking Python dependencies...
cd /d "%~dp0backend"
python -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r ../requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the WebSocket server
echo Starting WebSocket server...
echo Server will run on: ws://localhost:8765
echo.
echo To access the application:
echo 1. Open frontend/index.html in your browser
echo 2. Or use frontend/test-websocket.html for testing
echo.
echo Press Ctrl+C to stop the server
echo ========================================
python websocket_server.py

pause
