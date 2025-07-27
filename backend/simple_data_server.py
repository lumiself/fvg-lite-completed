#!/usr/bin/env python3
"""
Simple Data Server
HTTP-based server for providing real-time data
"""

from flask import Flask, jsonify
from flask_cors import CORS
import random
import json
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# Global data storage
current_data = {
    'ticks': [],
    'candles': [],
    'trade_suggestions': [],
    'market_bias': 'bullish',
    'last_update': datetime.utcnow().isoformat()
}

def generate_sample_data():
    """Generate sample data"""
    global current_data
    
    while True:
        try:
            # Generate sample tick
            tick = {
                'symbol': 'R_100',
                'quote': 1125.50 + (random.random() - 0.5) * 10,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Generate sample candles
            candles = []
            now = datetime.utcnow()
            base_price = 1125.50
            
            for i in range(20):
                candle_time = now - timedelta(minutes=i*5)
                price_change = (random.random() - 0.5) * 2
                open_price = base_price + price_change
                close_price = open_price + (random.random() - 0.5) * 1
                high_price = max(open_price, close_price) + random.random() * 0.5
                low_price = min(open_price, close_price) - random.random() * 0.5
                
                # Ensure all values are valid and properly formatted
                timestamp = int(candle_time.timestamp())
                open_val = round(open_price, 2)
                high_val = round(high_price, 2)
                low_val = round(low_price, 2)
                close_val = round(close_price, 2)
                
                # Validate the data before adding
                if (timestamp > 0 and 
                    open_val > 0 and high_val > 0 and low_val > 0 and close_val > 0 and
                    high_val >= max(open_val, close_val) and 
                    low_val <= min(open_val, close_val)):
                    
                    candles.append({
                        'timestamp': timestamp,
                        'open': open_val,
                        'high': high_val,
                        'low': low_val,
                        'close': close_val
                    })
            
            # Generate sample trade suggestions
            suggestions = [
                {
                    'direction': 'BUY',
                    'symbol': 'R_100',
                    'entry_price': '1125.50',
                    'stop_loss': '1120.00',
                    'take_profit': '1135.00',
                    'confidence': 85,
                    'reason': 'Silver Bullet setup: FVG + Liquidity sweep + MSS confluence'
                },
                {
                    'direction': 'SELL',
                    'symbol': 'frxEURUSD',
                    'entry_price': '1.0850',
                    'stop_loss': '1.0870',
                    'take_profit': '1.0800',
                    'confidence': 72,
                    'reason': 'Fair Value Gap detected with bearish bias'
                }
            ]
            
            # Update global data
            current_data.update({
                'ticks': [tick],
                'candles': candles,
                'trade_suggestions': suggestions,
                'market_bias': random.choice(['bullish', 'bearish', 'neutral']),
                'last_update': datetime.utcnow().isoformat()
            })
            
            # Wait 5 seconds before next update
            time.sleep(5)
            
        except Exception as e:
            print(f"Error generating data: {e}")
            time.sleep(5)

# Start data generation in background
data_thread = threading.Thread(target=generate_sample_data, daemon=True)
data_thread.start()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'data_available': True
    })

@app.route('/api/ticks', methods=['GET'])
def get_ticks():
    """Get current tick data"""
    return jsonify({
        'success': True,
        'data': current_data['ticks'],
        'timestamp': current_data['last_update']
    })

@app.route('/api/candles', methods=['GET'])
def get_candles():
    """Get current candle data"""
    candles = current_data['candles']
    print(f"Sending {len(candles)} candles")
    if candles:
        print(f"Sample candle: {candles[0]}")
    
    return jsonify({
        'success': True,
        'data': candles,
        'timestamp': current_data['last_update']
    })

@app.route('/api/trade_suggestions', methods=['GET'])
def get_trade_suggestions():
    """Get current trade suggestions"""
    return jsonify({
        'success': True,
        'suggestions': current_data['trade_suggestions'],
        'timestamp': current_data['last_update']
    })

@app.route('/api/market_bias', methods=['GET'])
def get_market_bias():
    """Get current market bias"""
    return jsonify({
        'success': True,
        'bias': current_data['market_bias'],
        'indicator': 'EMA(200)',
        'timestamp': current_data['last_update']
    })

@app.route('/api/liquidity_levels', methods=['GET'])
def get_liquidity_levels():
    """Get liquidity levels"""
    return jsonify({
        'success': True,
        'buy_side_liquidity': [],
        'sell_side_liquidity': [],
        'timestamp': current_data['last_update']
    })

if __name__ == '__main__':
    print("Starting Simple Data Server on http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001) 