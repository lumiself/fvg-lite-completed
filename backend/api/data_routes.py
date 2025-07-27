"""
Data API Routes
REST API endpoints for data retrieval and streaming
"""

from flask import Blueprint, jsonify, request
import asyncio
from datetime import datetime
import logging
from deriv_data_streamer import DerivDataStreamer, DataNormalizer

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)

# Global streamer instance
streamer = DerivDataStreamer()

@data_bp.route('/api/historical_data', methods=['GET'])
def get_historical_data():
    """Get historical candlestick data"""
    try:
        symbol = request.args.get('asset', 'frxEURUSD')
        timeframe = int(request.args.get('timeframe', 60))  # 60 = 1 minute
        lookback = int(request.args.get('lookback', 24))  # hours
        
        # Calculate count based on timeframe and lookback
        if timeframe == 60:  # 1 minute
            count = lookback * 60
        elif timeframe == 300:  # 5 minutes
            count = lookback * 12
        elif timeframe == 900:  # 15 minutes
            count = lookback * 4
        elif timeframe == 3600:  # 1 hour
            count = lookback
        else:
            count = 100
        
        candles = streamer.get_historical_candles(symbol, timeframe, count)
        
        return jsonify({
            'success': True,
            'data': candles,
            'symbol': symbol,
            'timeframe': timeframe,
            'count': len(candles),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/api/active_symbols', methods=['GET'])
def get_active_symbols():
    """Get list of active trading symbols"""
    try:
        symbols = streamer.get_active_symbols()
        
        # Filter for forex symbols
        forex_symbols = [s for s in symbols if s.get('market') == 'forex']
        
        return jsonify({
            'success': True,
            'data': forex_symbols,
            'count': len(forex_symbols),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting active symbols: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/api/test_connection', methods=['GET'])
def test_connection():
    """Test Deriv API connection"""
    try:
        # Test REST API
        symbols = streamer.get_active_symbols()
        
        return jsonify({
            'success': True,
            'message': 'Deriv API connection successful',
            'symbols_count': len(symbols),
            'config': {
                'app_id': streamer.ws_url.split('app_id=')[1] if 'app_id=' in streamer.ws_url else None,
                'api_token_configured': bool(streamer.api_token and streamer.api_token != 'your_api_token_here')
            }
        })
        
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (safe version)"""
    from config import DerivConfig
    
    config_status = DerivConfig.validate_config()
    
    return jsonify({
        'success': True,
        'config': {
            'app_id': DerivConfig.DERIV_APP_ID,
            'api_token_configured': DerivConfig.DERIV_API_TOKEN != 'your_api_token_here',
            'ws_url': DerivConfig.get_ws_url(),
            'is_valid': config_status['is_valid'],
            'issues': config_status['issues']
        }
    })

@data_bp.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration (for development/testing)"""
    try:
        data = request.json
        
        # Note: In production, this should update environment variables
        # For now, we'll just validate the new config
        
        new_app_id = data.get('app_id')
        new_api_token = data.get('api_token')
        
        response = {
            'success': True,
            'message': 'Configuration update received',
            'note': 'Restart application to apply changes',
            'new_config': {
                'app_id': new_app_id,
                'api_token_configured': bool(new_api_token)
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket endpoints placeholder
@data_bp.route('/api/ws/connect', methods=['POST'])
def ws_connect():
    """WebSocket connection status"""
    return jsonify({
        'success': True,
        'message': 'WebSocket endpoint ready',
        'url': 'ws://localhost:5000/ws/stream'
    })

# Error handlers for data routes
@data_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Data endpoint not found'
    }), 404

@data_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Data route error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
