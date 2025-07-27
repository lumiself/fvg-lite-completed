#!/bin/bash

echo "========================================"
echo "Deriv MCP Server Installation Script"
echo "========================================"
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2)
REQUIRED_VERSION="16.0.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Node.js version $NODE_VERSION is too old"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

echo "Node.js version: $NODE_VERSION ✓"
echo

echo "Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "Building the server..."
npm run build
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build the server"
    exit 1
fi

# Make the built file executable
chmod +x build/index.js

echo
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Get your Deriv App ID from: https://app.deriv.com/account/api-token"
echo "2. Get your API token (optional, for account operations)"
echo "3. Configure your MCP client with the path:"
echo "   $(pwd)/build/index.js"
echo
echo "To test the server:"
echo "node build/index.js"
echo
