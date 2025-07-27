#!/usr/bin/env python3
"""
Test Deriv API with official endpoints
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_official_deriv_api():
    """Test using Deriv's official API endpoints"""
    
    # Test using the official Deriv API
    url = "https://api.deriv.com/api"
    
    # Test active symbols
    payload = {
        "active_symbols": "brief",
        "product_type": "basic"
    }
    
    try:
        logger.info("Testing Deriv API with official endpoint...")
        
        # Try different endpoints
        endpoints = [
            "https://api.deriv.com/api",
            "https://api.deriv.com/websockets/v3",
            "https://ws.derivws.com/websockets/v3",
            "https://ws.binaryws.com/websockets/v3"
        ]
        
        for endpoint in endpoints:
            logger.info(f"Testing endpoint: {endpoint}")
            try:
                response = requests.post(endpoint, json=payload, timeout=10)
                logger.info(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"  Response: {data}")
                    
                    if "active_symbols" in data:
                        symbols = data["active_symbols"]
                        logger.info(f"  SUCCESS: Found {len(symbols)} symbols")
                        return symbols
                    elif "error" in data:
                        logger.info(f"  Error: {data['error']}")
                    else:
                        logger.info(f"  Unexpected response: {data}")
                else:
                    logger.info(f"  HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                logger.error(f"  Error with {endpoint}: {e}")
    
    except Exception as e:
        logger.error(f"General error: {e}")
    
    return []

def test_simple_request():
    """Test with a very simple request"""
    
    # Test with app_id=1 (Deriv's public testing app)
    url = "https://ws.binaryws.com/websockets/v3?app_id=1"
    
    payload = {
        "active_symbols": "brief"
    }
    
    try:
        logger.info("Testing simple request...")
        response = requests.post(url, json=payload, timeout=10)
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            return data
            
    except Exception as e:
        logger.error(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    logger.info("Testing Deriv API with official endpoints...")
    test_official_deriv_api()
    result = test_simple_request()
    
    if result:
        logger.info(f"Final result: {result}")
