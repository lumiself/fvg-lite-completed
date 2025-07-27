# Deriv MCP Server - Complete Installation Guide

## 📦 Package Contents

Your `deriv-mcp-server-copy` directory contains:
- `package.json` - Project configuration and dependencies
- `tsconfig.json` - TypeScript configuration
- `src/index.ts` - Main server source code
- `README.md` - Comprehensive documentation
- `CONFIGURATION.md` - MCP client configuration examples
- `install.bat` - Windows installation script
- `install.sh` - Unix/Linux installation script
- `.gitignore` - Git ignore rules

## 🚀 Quick Start (2 minutes)

### Option 1: Automated Installation

#### Windows
```cmd
cd deriv-mcp-server-copy
install.bat
```

#### macOS/Linux
```bash
cd deriv-mcp-server-copy
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Build the server:**
   ```bash
   npm run build
   ```

3. **Test the server:**
   ```bash
   node build/index.js
   ```

## 📋 Step-by-Step Installation

### Step 1: Prerequisites
- **Node.js 16+** installed
- **Internet connection** for API access
- **MCP-compatible client** (Claude Desktop, Cursor, VS Code)

### Step 2: Get Deriv Credentials
1. **App ID**: Go to https://app.deriv.com/account/api-token
   - Use `1089` for testing (public app ID)
   - Or create your own application

2. **API Token** (optional):
   - Create a token with **Read** and **Trade** permissions
   - Required for account operations and trading

### Step 3: Install & Build
```bash
# Navigate to the directory
cd deriv-mcp-server-copy

# Install dependencies
npm install

# Build TypeScript to JavaScript
npm run build
```

### Step 4: Configure MCP Client

#### Claude Desktop (Windows)
File: `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["C:\\full\\path\\to\\deriv-mcp-server\\build\\index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### Claude Desktop (macOS/Linux)
File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
File: `~/.config/Claude/claude_desktop_config.json` (Linux)
```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["/full/path/to/deriv-mcp-server/build/index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Step 5: Test Connection
1. **Restart your MCP client** (Claude Desktop, Cursor, etc.)
2. **Test the connection** using the `test_connection` tool
3. **Verify tools are available** in your client

## 🔧 Available Tools

After installation, you'll have access to these tools:

| Tool | Description | Requires API Token |
|------|-------------|-------------------|
| `get_active_symbols` | List all trading symbols | ❌ |
| `get_historical_candles` | Get OHLCV candlestick data | ❌ |
| `get_tick_data` | Real-time price ticks | ❌ |
| `get_trading_times` | Market hours and schedules | ❌ |
| `get_contracts_for_symbol` | Available contract types | ❌ |
| `get_account_balance` | Account balance info | ✅ |
| `get_portfolio` | Open positions | ✅ |
| `get_statement` | Transaction history | ✅ |
| `buy_contract` | Place trades | ✅ |
| `sell_contract` | Close positions | ✅ |
| `test_connection` | Verify API connectivity | ❌ |
| `get_server_time` | Current server time | ❌ |

## 🎯 Example Usage

### Basic Market Data
```json
{
  "name": "get_active_symbols",
  "arguments": {
    "market": "synthetic_index"
  }
}
```

### Historical Data
```json
{
  "name": "get_historical_candles",
  "arguments": {
    "symbol": "R_50",
    "timeframe": 3600,
    "count": 50
  }
}
```

### Account Operations (with API token)
```json
{
  "name": "get_account_balance"
}
```

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **"Node.js not found"** | Install Node.js 16+ from https://nodejs.org/ |
| **"Module not found"** | Run `npm install` to install dependencies |
| **"Permission denied"** | Run `chmod +x build/index.js` (Linux/macOS) |
| **"Invalid path"** | Use absolute paths in configuration |
| **"Connection failed"** | Check internet connection and Deriv API status |

### Debug Steps
1. **Test basic connectivity:**
   ```bash
   node build/index.js
   ```
2. **Check Node.js version:**
   ```bash
   node --version
   ```
3. **Verify build:**
   ```bash
   ls -la build/
   ```

## 📞 Getting Help

- **Documentation**: See `README.md` for detailed API documentation
- **Configuration**: See `CONFIGURATION.md` for client-specific setup
- **Deriv API**: https://api.deriv.com/docs/
- **Support**: https://deriv.com/contact-us

## ✅ Installation Checklist

- [ ] Node.js 16+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] Server built (`npm run build`)
- [ ] MCP client configured
- [ ] Environment variables set
- [ ] Connection tested
- [ ] Tools verified working

## 🔄 Next Steps

1. **Explore the API** using the available tools
2. **Set up API token** for account operations
3. **Integrate with your trading strategy**
4. **Monitor rate limits** (120 req/min public, 60 req/min authenticated)

## 📦 Directory Structure After Installation

```
deriv-mcp-server-copy/
├── node_modules/          # Dependencies
├── build/                 # Compiled JavaScript
│   ├── index.js          # Main server file
│   ├── index.d.ts        # TypeScript declarations
│   └── *.map             # Source maps
├── src/                  # TypeScript source
│   └── index.ts          # Main source file
├── package.json          # Project configuration
├── tsconfig.json         # TypeScript config
├── README.md            # Full documentation
├── CONFIGURATION.md     # MCP client configs
├── install.bat          # Windows installer
├── install.sh           # Unix/Linux installer
└── .gitignore          # Git ignore rules
```

## 🎉 You're Ready!

Your Deriv MCP server is now installed and ready to use. Start exploring the markets with comprehensive trading data and analysis tools!
