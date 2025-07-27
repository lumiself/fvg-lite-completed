# 🎯 FVG Silver Bullet Lite

[![CI/CD](https://github.com/yourusername/fvg-silver-bullet-lite/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/fvg-silver-bullet-lite/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![WebSocket](https://img.shields.io/badge/WebSocket-8765-green.svg)](http://localhost:8765)

A lightweight, real-time trading signal system that provides live market analysis and trading signals through WebSocket-based architecture.

## ✨ Features

- **🔴 Real-time Trading Signals** - Live FVG (Fair Value Gap) detection
- **📊 Market Analysis Engine** - Advanced market bias and liquidity analysis
- **🌐 WebSocket Communication** - Real-time data streaming
- **📱 Responsive Web Interface** - Works on all devices
- **🎨 Dark/Light Theme Support** - User preference themes
- **⚡ Auto-reconnection** - Robust connection handling
- **🧪 Built-in Testing Tools** - WebSocket connection testing
- **🚀 Cross-platform** - Windows, macOS, Linux compatible

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

#### Option 1: One-Click Start
**Windows:**
```bash
# Double-click or run in terminal
start.bat
```

**Linux/macOS:**
```bash
# Make executable and run
chmod +x start.sh
./start.sh
```

#### Option 2: Manual Setup
```bash
# Clone repository
git clone https://github.com/yourusername/fvg-silver-bullet-lite.git
cd fvg-silver-bullet-lite

# Install dependencies
pip install -r requirements.txt

# Start server
cd backend
python websocket_server.py

# Open in browser
# Navigate to frontend/index.html
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | `frontend/index.html` | Full trading interface |
| **WebSocket Test** | `frontend/test-websocket.html` | Connection testing |
| **WebSocket URL** | `ws://localhost:8765` | Server endpoint |

## 📊 System Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Web Client    │ ◄──────────────► │ Python Server   │
│   (frontend)    │   ws://:8765    │   (backend)     │
└─────────────────┘                 └─────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────┐                 ┌─────────────────┐
│   Responsive    │                 │   Analysis      │
│   UI/UX         │                 │   Engine        │
└─────────────────┘                 └─────────────────┘
```

## 🎯 Usage

### Starting the System
1. **Run startup script** (start.bat or start.sh)
2. **Wait for "WebSocket server started"** message
3. **Open frontend/index.html** in browser
4. **Click "Connect"** to establish WebSocket connection

### Using the Application
- **Signal Feed**: Real-time trading signals appear here
- **Market Overview**: Shows volatility, active pairs, signal strength
- **Settings**: Configure WebSocket URL, sound alerts, auto-scroll
- **Quick Actions**: Toggle sound, theme, export signals

## 🛠️ Development

### Project Structure
```
fvg-silver-bullet-lite/
├── backend/
│   ├── websocket_server.py    # Main WebSocket server
│   ├── analysis/              # FVG detection algorithms
│   ├── api/                   # REST endpoints
│   └── database/              # SQLite storage
├── frontend/
│   ├── index.html            # Main application
│   ├── app.js                # Application logic
│   ├── styles.css            # Responsive styling
│   └── src/                  # Modular components
├── .github/                  # GitHub workflows & templates
└── docs/                     # Additional documentation
```

### Contributing
We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Fork and clone
git clone https://github.com/yourusername/fvg-silver-bullet-lite.git
cd fvg-silver-bullet-lite

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_installation.py

# Start development server
cd backend && python websocket_server.py
```

## 🔧 Configuration

### WebSocket Settings
- **Port**: 8765 (configurable)
- **Host**: localhost
- **Protocol**: ws://

### Environment Variables
```bash
# Optional configuration
export WEBSOCKET_PORT=8765
export LOG_LEVEL=INFO
```

## 📈 Features in Detail

### Analysis Engine
- **FVG Detection**: Identifies Fair Value Gaps in market data
- **Liquidity Analysis**: Analyzes market liquidity levels
- **Market Bias**: Determines overall market direction
- **Signal Generation**: Creates actionable trading signals

### Web Interface
- **Real-time Updates**: Live signal streaming
- **Responsive Design**: Mobile-first approach
- **Theme Support**: Dark/light mode toggle
- **Connection Status**: Visual connection indicators
- **Signal History**: Track past signals

## 🧪 Testing

### Backend Testing
```bash
# Run verification script
python verify_installation.py

# Test WebSocket server
cd backend && python -c "from websocket_server import WebSocketServer"
```

### Frontend Testing
- Open `frontend/test-websocket.html`
- Test WebSocket connection
- Verify signal reception

## 🔍 Troubleshooting

### Common Issues
1. **WebSocket Connection Failed**
   - Check if server is running
   - Verify port 8765 is available
   - Use test-websocket.html for diagnosis

2. **Python Dependencies**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Browser Issues**
   - Clear browser cache
   - Try incognito/private mode
   - Check browser console (F12)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🙏 Acknowledgments

- Built with Python and vanilla JavaScript
- Inspired by trading community needs
- Designed for simplicity and effectiveness

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/fvg-silver-bullet-lite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fvg-silver-bullet-lite/discussions)
- **Documentation**: Check [README.md](README.md)

---

**Made with ❤️ for the trading community**
