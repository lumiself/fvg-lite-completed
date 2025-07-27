#!/usr/bin/env python3
"""
Test Deriv API symbol retrieval
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deriv_api_direct():
    """Test Deriv API directly to see available symbols"""
    
    # Test active symbols endpoint
    url = "https://api.deriv.com/websockets/v3"
    
    # Test with different product types
    product_types = ['basic', 'multiplier', 'options']
    
    for product_type in product_types:
        payload = {
            "active_symbols": "brief",
            "product_type": product_type
        }
        
        try:
            logger.info(f"Testing product type: {product_type}")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "active_symbols" in data:
                    symbols = data["active_symbols"]
                    logger.info(f"Found {len(symbols)} symbols for {product_type}")
                    
                    # Show some examples
                    forex_symbols = [s for s in symbols if s.get('market') == 'forex']
                    synthetic_symbols = [s for s in symbols if s.get('market') == 'synthetic_index']
                    
                    logger.info(f"Forex symbols: {len(forex_symbols)}")
                    logger.info(f"Synthetic symbols: {len(synthetic_symbols)}")
                    
                    if synthetic_symbols:
                        logger.info("Synthetic indices available:")
                        for symbol in synthetic_symbols[:5]:
                            logger.info(f"  - {symbol['symbol']}: {symbol.get('display_name', symbol['symbol'])}")
                    
                    if forex_symbols:
                        logger.info("Forex symbols available:")
                        for symbol in forex_symbols[:5]:
                            logger.info(f"  - {symbol['symbol']}: {symbol.get('display_name', symbol['symbol'])}")
                else:
                    logger.error(f"No active_symbols in response for {product_type}: {data}")
            else:
                logger.error(f"HTTP {response.status_code} for {product_type}")
                
        except Exception as e:
            logger.error(f"Error testing {product_type}: {e}")

def test_websocket_format():
    """Test the exact format used in the streamer"""
    from deriv_data_streamer import DerivDataStreamer
    
    streamer = DerivDataStreamer()
    symbols = streamer.get_active_symbols()
    logger.info(f"Streamer returned {len(symbols)} symbols")
    
    if symbols:
        for symbol in symbols[:10]:
            logger.info(f"Symbol: {symbol}")

if __name__ == "__main__":
    logger.info("Testing Deriv API symbol retrieval...")
    test_deriv_api_direct()
    test_websocket_format()
