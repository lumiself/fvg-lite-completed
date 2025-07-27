#!/usr/bin/env python3
"""
Test Deriv API with correct format
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deriv_api_correct():
    """Test Deriv API with correct WebSocket format"""
    
    # Test using WebSocket endpoint with POST for active symbols
    url = "https://ws.derivws.com/websockets/v3"
    
    payload = {
        "active_symbols": "brief",
        "product_type": "basic"
    }
    
    try:
        logger.info("Testing active symbols with correct endpoint...")
        response = requests.post(url, json=payload, timeout=10)
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            if "active_symbols" in data:
                symbols = data["active_symbols"]
                logger.info(f"Found {len(symbols)} total symbols")
                
                # Show market breakdown
                markets = {}
                for symbol in symbols:
                    market = symbol.get('market', 'unknown')
                    if market not in markets:
                        markets[market] = []
                    markets[market].append(symbol['symbol'])
                
                for market, symbols_list in markets.items():
                    logger.info(f"{market}: {len(symbols_list)} symbols")
                    if symbols_list:
                        logger.info(f"  Examples: {symbols_list[:3]}")
                
                return symbols
            else:
                logger.error(f"No active_symbols in response: {data}")
        else:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    
    return []

def test_historical_data():
    """Test historical data endpoint"""
    url = "https://ws.derivws.com/websockets/v3"
    
    payload = {
        "candles": 1,
        "symbol": "R_50",  # Volatility 50 Index (synthetic, trades 24/7)
        "granularity": 3600,
        "count": 10,
        "style": "candles"
    }
    
    try:
        logger.info("Testing historical data...")
        response = requests.post(url, json=payload, timeout=10)
        
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "candles" in data:
                candles = data["candles"]
                logger.info(f"Found {len(candles)} candles for R_50")
                if candles:
                    logger.info(f"Latest candle: {candles[-1]}")
                return candles
            else:
                logger.error(f"No candles in response: {data}")
        else:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    
    return []

if __name__ == "__main__":
    logger.info("Testing Deriv API with correct format...")
    symbols = test_deriv_api_correct()
    candles = test_historical_data()
    
    logger.info(f"Test completed. Symbols: {len(symbols)}, Candles: {len(candles)}")
