@echo off
echo Starting FVG Silver Bullet WebSocket Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0backend"

echo Starting WebSocket server on port 8765...
echo.
echo Server will be available at: ws://localhost:8765
echo.
echo To test the connection:
echo 1. Open frontend/test-websocket.html in your browser
echo 2. Or open frontend/index.html for the full application
echo.

python websocket_server.py

pause
