# MCP Configuration Examples

This file provides ready-to-use configuration examples for different MCP clients.

## 🖥️ Claude Desktop

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["C:\\Users\\YourUsername\\deriv-mcp-server\\build\\index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["/Users/yourusername/deriv-mcp-server/build/index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### Linux
Location: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "deriv": {
      "command": "node",
      "args": ["/home/yourusername/deriv-mcp-server/build/index.js"],
      "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

## 🎯 Cursor IDE

### Settings.json (Global)
Location: Open Command Palette → "Preferences: Open Settings (JSON)"

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

### Workspace Settings
Create `.cursor/settings.json` in your project:

```json
{
  "mcp": {
    "servers": {
      "deriv": {
        "command": "node",
        "args": ["./deriv-mcp-server/build/index.js"],
        "env": {
          "DERIV_APP_ID": "1089",
          "DERIV_API_TOKEN": "your_api_token_here"
        }
      }
    }
  }
}
```

## 🔧 VS Code

### Settings.json
Open Command Palette → "Preferences: Open Settings (JSON)"

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

## 🐍 Python MCP Client

### Using mcp package
```python
from mcp import Client

client = Client()
await client.connect_to_server({
    "command": "node",
    "args": ["/path/to/deriv-mcp-server/build/index.js"],
    "env": {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "your_api_token_here"
    }
})
```

## 🔍 Finding Your Paths

### Windows
```cmd
# Get current directory
cd /d "C:\path\to\deriv-mcp-server"
echo %CD%

# Test the path
node "%CD%\build\index.js"
```

### macOS/Linux
```bash
# Get current directory
cd /path/to/deriv-mcp-server
pwd

# Test the path
node "$(pwd)/build/index.js"
```

## 🧪 Testing Configuration

### Quick Test
1. Run the server directly:
   ```bash
   node build/index.js
   ```
2. You should see: "Deriv MCP server v2.0.0 running..."

### Test with MCP Client
Use the `test_connection` tool to verify everything works:
```json
{
  "name": "test_connection",
  "arguments": {}
}
```

## 🔐 Environment Variables

### Required
- `DERIV_APP_ID`: Your Deriv app ID (use `1089` for testing)

### Optional
- `DERIV_API_TOKEN`: Your Deriv API token (for account operations)

### Setting Environment Variables

#### Windows (Command Prompt)
```cmd
set DERIV_APP_ID=1089
set DERIV_API_TOKEN=your_token_here
```

#### Windows (PowerShell)
```powershell
$env:DERIV_APP_ID="1089"
$env:DERIV_API_TOKEN="your_token_here"
```

#### macOS/Linux
```bash
export DERIV_APP_ID=1089
export DERIV_API_TOKEN=your_token_here
```

## 📝 Common Issues

### Path Issues
- **Windows**: Use double backslashes `\\` or forward slashes `/`
- **Spaces in path**: Wrap the entire path in quotes

### Permission Issues
- **Linux/macOS**: Run `chmod +x build/index.js`
- **Windows**: Ensure Node.js is in PATH

### Network Issues
- Ensure internet connection
- Check firewall settings
- Verify Deriv API is accessible

## 🔄 Restarting MCP Clients

After configuration changes:
1. **Claude Desktop**: Restart the application
2. **Cursor**: Reload window (Ctrl/Cmd + Shift + P → "Developer: Reload Window")
3. **VS Code**: Reload window (Ctrl/Cmd + Shift + P → "Developer: Reload Window")
