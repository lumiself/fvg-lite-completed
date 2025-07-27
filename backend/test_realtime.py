#!/usr/bin/env python3
"""
Test Real-time Data Streaming
Test script to verify Deriv API WebSocket connection and data streaming
"""

import asyncio
import json
import logging
from datetime import datetime
from deriv_data_streamer import DerivDataStreamer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tick_streaming():
    """Test real-time tick streaming"""
    streamer = DerivDataStreamer()
    
    # Connect to Deriv API
    if not await streamer.connect():
        logger.error("Failed to connect to Deriv API")
        return
    
    logger.info("Connected to Deriv API successfully")
    
    # Test tick subscription
    async def tick_handler(tick):
        logger.info(f"Received tick: {tick}")
    
    await streamer.subscribe_to_ticks("frxEURUSD", tick_handler)
    
    # Keep running for 30 seconds
    logger.info("Listening for ticks for 30 seconds...")
    await asyncio.sleep(30)
    
    await streamer.disconnect()
    logger.info("Test completed")

async def test_candle_streaming():
    """Test real-time candle streaming"""
    streamer = DerivDataStreamer()
    
    # Connect to Deriv API
    if not await streamer.connect():
        logger.error("Failed to connect to Deriv API")
        return
    
    logger.info("Connected to Deriv API successfully")
    
    # Test candle subscription (1 hour candles)
    async def candle_handler(candles):
        logger.info(f"Received candles: {len(candles)} candles")
        if candles:
            latest = candles[-1]
            logger.info(f"Latest candle: {latest}")
    
    await streamer.subscribe_to_candles("frxEURUSD", 3600, candle_handler)
    
    # Keep running for 30 seconds
    logger.info("Listening for candles for 30 seconds...")
    await asyncio.sleep(30)
    
    await streamer.disconnect()
    logger.info("Test completed")

async def test_historical_data():
    """Test historical data retrieval"""
    streamer = DerivDataStreamer()
    
    # Get historical candles
    candles = streamer.get_historical_candles("frxEURUSD", 3600, 10)
    
    logger.info(f"Retrieved {len(candles)} historical candles")
    for i, candle in enumerate(candles):
        logger.info(f"Candle {i+1}: {candle}")

async def main():
    """Run all tests"""
    logger.info("Starting real-time data tests...")
    
    # Test historical data first
    await test_historical_data()
    
    # Test real-time streaming
    await test_tick_streaming()
    await test_candle_streaming()
    
    logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(main()) 