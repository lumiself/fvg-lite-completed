@echo off
echo ========================================
echo Deriv MCP Server Installation Script
echo ========================================
echo.

echo Checking Node.js version...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Building the server...
npm run build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build the server
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get your Deriv App ID from: https://app.deriv.com/account/api-token
echo 2. Get your API token (optional, for account operations)
echo 3. Configure your MCP client with the path:
echo    %CD%\build\index.js
echo.
echo To test the server:
echo node build\index.js
echo.
pause
