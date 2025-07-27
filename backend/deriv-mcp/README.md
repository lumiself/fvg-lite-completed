# Deriv MCP Server v2.0.0

A comprehensive Model Context Protocol (MCP) server for Deriv API integration, providing access to trading data, market analysis, and account management capabilities.

## 🚀 Features

### 📊 Market Data
- **Real-time tick data** with bid/ask/quote prices
- **Historical candlestick data** (OHLCV format)
- **Active trading symbols** across all markets
- **Trading times** for symbols and markets
- **Contract specifications** for each symbol

### 💰 Account Management
- **Account balance** and currency information
- **Portfolio overview** with open positions
- **Transaction statements** with filtering options
- **Real-time position updates**

### 🔄 Trading Operations
- **Buy contracts** with various types (CALL, PUT, ASIAN, etc.)
- **Sell/close positions** instantly
- **Contract parameters** validation
- **Risk management** tools

### 📈 Market Analysis
- **Market status** (open/closed)
- **Symbol information** with pip sizes
- **Contract availability** per symbol
- **Server time synchronization**

## 📋 API Documentation Integration

This server incorporates complete Deriv API documentation including:

### Supported Markets
- **Forex**: EUR/USD, GBP/USD, USD/JPY, etc.
- **Synthetic Indices**: R_50, R_100, R_500, etc. (24/7 trading)
- **Commodities**: Gold, Silver, Oil
- **Stock Indices**: US_30, US_100, US_500
- **Cryptocurrencies**: BTC/USD, ETH/USD, etc.

### Timeframes
- **1 minute**: 60 seconds
- **5 minutes**: 300 seconds
- **15 minutes**: 900 seconds
- **30 minutes**: 1800 seconds
- **1 hour**: 3600 seconds
- **4 hours**: 14400 seconds
- **1 day**: 86400 seconds

### Contract Types
- **CALL/PUT**: Rise/Fall contracts
- **ASIAN**: Asian options
- **DIGITMATCH/DIFFER**: Digit contracts
- **TOUCH/NOTOUCH**: Touch/No-touch contracts
- **HIGHER/LOWER**: Higher/Lower contracts

## 🔧 Installation & Configuration

### Prerequisites
- Node.js 16+ 
- Deriv App ID (get from https://app.deriv.com/account/api-token)

### Quick Installation

#### 1. Clone or Download
```bash
# Option A: Clone from repository
git clone https://github.com/your-org/deriv-mcp-server.git
cd deriv-mcp-server

# Option B: Copy the directory
# Copy the entire deriv-mcp-server-copy directory to your target computer
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Build the Server
```bash
npm run build
```

#### 4. Test the Installation
```bash
npm run start
```
You should see: "Deriv MCP server v2.0.0 running with comprehensive API documentation"

## 🛠️ MCP Configuration

### For Claude Desktop (claude_desktop_config.json)

#### Windows
```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["C:\\path\\to\\deriv-mcp-server\\build\\index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

#### macOS/Linux
```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["/path/to/deriv-mcp-server/build/index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### For Cursor IDE (settings.json)
```json
{
  "mcp": {
    "servers": {
      "deriv": {
        "command": "node",
        "args": ["/path/to/deriv-mcp-server/build/index.js"],
        "env": {
          "DERIV_APP_ID": "1089",
          "DERIV_API_TOKEN": "your_api_token_here"
        }
      }
    }
  }
}
```

### For VS Code (settings.json)
```json
{
  "mcp": {
    "servers": {
      "deriv": {
        "command": "node",
        "args": ["/path/to/deriv-mcp-server/build/index.js"],
        "env": {
          "DERIV_APP_ID": "1089",
          "DERIV_API_TOKEN": "your_api_token_here"
        }
      }
    }
  }
}
```

## 🎯 Getting Started

### 1. Get Your Deriv App ID
1. Go to https://app.deriv.com/account/api-token
2. Create a new application or use the default app ID: `1089`
3. Copy your App ID

### 2. Get Your API Token (Optional)
1. Go to https://app.deriv.com/account/api-token
2. Create a new token with appropriate permissions:
   - **Read**: Account balance, portfolio, statement
   - **Trade**: Buy/sell contracts
3. Copy your API token

### 3. Test Connection
```bash
# Test basic connection (no API token required)
node build/index.js
```

## 🛠️ Usage Examples

### Basic Market Data

**Get active symbols**:
```json
{
  "name": "get_active_symbols",
  "arguments": {
    "market": "synthetic_index"
  }
}
```

**Get historical candles**:
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

**Get tick data**:
```json
{
  "name": "get_tick_data",
  "arguments": {
    "symbol": "frxEURUSD",
    "count": 10
  }
}
```

### Account Operations (requires API token)

**Get account balance**:
```json
{
  "name": "get_account_balance"
}
```

**Get portfolio**:
```json
{
  "name": "get_portfolio"
}
```

**Get statement**:
```json
{
  "name": "get_statement",
  "arguments": {
    "limit": 20,
    "date_from": "2024-01-01"
  }
}
```

### Trading Operations (requires API token)

**Buy a contract**:
```json
{
  "name": "buy_contract",
  "arguments": {
    "symbol": "R_50",
    "contract_type": "CALL",
    "duration": 300,
    "amount": 10
  }
}
```

**Sell a position**:
```json
{
  "name": "sell_contract",
  "arguments": {
    "contract_id": "123456789"
  }
}
```

## 📊 Rate Limits

- **Public endpoints**: 120 requests per minute
- **Authenticated endpoints**: 60 requests per minute
- **Real-time subscriptions**: Unlimited (WebSocket)

## 🔐 Security

- **API tokens** are never logged or exposed
- **Environment variables** for sensitive data
- **Rate limiting** built-in
- **Error handling** with detailed messages

## 📝 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DERIV_APP_ID` | Your Deriv app ID | `1089` | No |
| `DERIV_API_TOKEN` | Your Deriv API token | `""` | No (only for account operations) |

## 🔗 API References

- **Deriv API Documentation**: https://api.deriv.com/docs/
- **WebSocket API**: https://api.deriv.com/websockets
- **Contract Types**: https://api.deriv.com/examples/contracts
- **Market Hours**: https://api.deriv.com/examples/trading-times

## 🐛 Troubleshooting

### Common Issues

1. **"InvalidAppID" error**:
   - Verify your DERIV_APP_ID is correct
   - Use public app ID `1089` for testing

2. **"Authorization failed"**:
   - Check your DERIV_API_TOKEN
   - Ensure token has necessary permissions

3. **"Market is closed"**:
   - Use synthetic indices (R_50, R_100) for 24/7 trading
   - Check trading times with `get_trading_times`

4. **"Invalid parameters"**:
   - Verify symbol format (e.g., "frxEURUSD", "R_50")
   - Check duration units and values

### Debug Mode
Enable debug logging by setting:
```bash
export DEBUG=deriv-mcp-server
```

### Installation Issues

#### Node.js Version
Ensure you have Node.js 16+:
```bash
node --version
```

#### Permission Issues (Linux/macOS)
```bash
chmod +x build/index.js
```

#### Windows Path Issues
Use double backslashes in paths:
```json
"C:\\Users\\username\\deriv-mcp-server\\build\\index.js"
```

## 📞 Support

- **Deriv Support**: https://deriv.com/contact-us
- **API Issues**: Check https://api.deriv.com/docs/
- **GitHub Issues**: Report bugs and feature requests

## 🔄 Updates

This server is regularly updated to include:
- New Deriv API endpoints
- Enhanced error handling
- Performance improvements
- Additional market data

## 📦 Package Scripts

| Script | Description |
|--------|-------------|
| `npm run build` | Build the TypeScript project |
| `npm run dev` | Watch mode for development |
| `npm run start` | Start the server |
| `npm run clean` | Clean build directory |
| `npm run rebuild` | Clean and rebuild |

## 🌐 Network Requirements

- **Internet connection** required
- **WebSocket support** for real-time data
- **HTTPS/443** for API calls
- **WSS/443** for WebSocket connections

## 🎯 Quick Test Commands

After installation, test these commands:

```bash
# Test connection
node build/index.js

# Test with MCP client
# Use the test_connection tool to verify everything works
```

## 📋 Installation Checklist

- [ ] Node.js 16+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] Project built (`npm run build`)
- [ ] MCP configuration updated
- [ ] Environment variables set
- [ ] Connection tested
- [ ] Tools verified working
