#!/usr/bin/env python3
"""
Test Deriv API without app ID
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deriv_no_appid():
    """Test Deriv API without app ID"""
    
    # Test using WebSocket endpoint without app ID
    url = "https://ws.derivws.com/websockets/v3"
    
    payload = {
        "active_symbols": "brief",
        "product_type": "basic"
    }
    
    try:
        logger.info("Testing active symbols without app ID...")
        response = requests.post(url, json=payload, timeout=10)
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Response data: {data}")
            return data
        else:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    
    return None

def test_with_different_appid():
    """Test with various common app IDs"""
    
    app_ids = ['1089', '1', '1234', '9999', '1000']
    
    for app_id in app_ids:
        url = f"https://ws.derivws.com/websockets/v3?app_id={app_id}"
        
        payload = {
            "active_symbols": "brief",
            "product_type": "basic"
        }
        
        try:
            logger.info(f"Testing with app_id={app_id}")
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    logger.info(f"SUCCESS with app_id={app_id}")
                    logger.info(f"Found {len(data.get('active_symbols', []))} symbols")
                    return data
                else:
                    logger.info(f"Error with app_id={app_id}: {data.get('error')}")
            else:
                logger.info(f"HTTP {response.status_code} with app_id={app_id}")
                
        except Exception as e:
            logger.error(f"Error with app_id={app_id}: {e}")
    
    return None

if __name__ == "__main__":
    logger.info("Testing Deriv API with various configurations...")
    test_deriv_no_appid()
    test_with_different_appid()
