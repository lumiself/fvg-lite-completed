#!/usr/bin/env python3
"""
FVG Silver Bullet Lite - Installation Verification Script
Run this script to verify the installation is complete and working
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.7+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} is too old. Need 3.7+")
        return False
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'websockets',
        'requests',
        'pandas',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'backend/websocket_server.py',
        'backend/requirements.txt',
        'frontend/index.html',
        'frontend/styles.css',
        'frontend/app.js',
        'frontend/test-websocket.html',
        'requirements.txt',
        'start.bat',
        'start.sh',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def check_websocket_server():
    """Test if the WebSocket server can be imported"""
    try:
        sys.path.insert(0, 'backend')
        from websocket_server import WebSocketServer
        print("✅ WebSocket server can be imported")
        return True
    except ImportError as e:
        print(f"❌ Cannot import WebSocket server: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🔍 FVG Silver Bullet Lite - Installation Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("WebSocket Server", check_websocket_server)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Installation is ready.")
        print("\nNext steps:")
        print("1. Run 'start.bat' (Windows) or './start.sh' (Linux/Mac)")
        print("2. Open 'frontend/index.html' in your browser")
        print("3. Click 'Connect' to establish WebSocket connection")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
