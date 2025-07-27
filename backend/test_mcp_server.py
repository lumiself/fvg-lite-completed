#!/usr/bin/env python3
"""
Test the Deriv MCP server functionality
"""

import subprocess
import json
import sys
import os

def test_mcp_server():
    """Test the Deriv MCP server"""
    
    # Test the connection
    print("Testing Deriv MCP server...")
    
    # Change to the MCP server directory
    os.chdir("C:\\Users\\DELL\\Documents\\Cline\\MCP\\deriv-mcp-server")
    
    # Test the test_connection tool
    test_input = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "test_connection",
            "arguments": {}
        }
    }
    
    try:
        # Run the MCP server with the test input
        process = subprocess.Popen(
            ["node", "build/index.js"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the test request
        process.stdin.write(json.dumps(test_input) + "\n")
        process.stdin.flush()
        
        # Read the response
        response = process.stdout.readline()
        result = json.loads(response)
        
        print("Connection test result:")
        print(json.dumps(result, indent=2))
        
        # Test active symbols
        symbols_input = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_active_symbols",
                "arguments": {"market": "synthetic_index"}
            }
        }
        
        process.stdin.write(json.dumps(symbols_input) + "\n")
        process.stdin.flush()
        
        symbols_response = process.stdout.readline()
        symbols_result = json.loads(symbols_response)
        
        print("\nActive symbols test result:")
        print(json.dumps(symbols_result, indent=2))
        
        # Clean up
        process.terminate()
        
    except Exception as e:
        print(f"Error testing MCP server: {e}")

if __name__ == "__main__":
    test_mcp_server()
